from functools import partial

from django.shortcuts import get_object_or_404
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, Spacer, TableStyle
from reportlab.lib.units import inch, mm, cm
from .models import SzamlaTetel, SzamlaTorzs, Ceg, Vevo, Afa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        '''
        self.drawRightString(211 * mm, 15 * mm + (0.2 * inch),
                             "Page %d of %d" % (self._pageNumber, page_count))
        '''
        self.drawRightString(205 * mm, 5 * mm + (0.2 * inch),
                             "%d oldal{oszesen: %d}" % (page_count, self._pageNumber))


class MyPrint:
    def __init__(self, buffer, pagesize, peldany):
        # Register Fonts
        #pdfmetrics.registerFont(TTFont('Arial-Bold', settings.STATIC_ROOT + 'fonts/arialbd.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSerifB', 'DejaVuSerif-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSerifI', 'DejaVuSerif-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSerifBI', 'DejaVuSerif-BoldItalic.ttf'))
        pdfmetrics.registerFontFamily('DejaVuSerif', normal='DejaVuSerif', bold='DejaVuSerifB', italic='DejaVuSerifI',
                                      boldItalic='DejaVuSerifBI')

        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
        if peldany == '2':
           self.peldany = '3.2_Könyvelés példánya'
        elif peldany == '3':
           self.peldany = '3.3_Vevőnyilvántartás példánya'
        elif peldany == '1':
           self.peldany = '3.1_Eredeti példány'

    @staticmethod
    def _header_footer(canvas, doc, custom_footer):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header = Paragraph('Header' * 1, styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        # Footer
        footer = Paragraph(custom_footer * 1, styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

    def print_invoice(self, vszamlaszam):

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=cm/6,
                                leftMargin=cm/6,
                                topMargin=cm/6,
                                bottomMargin=cm/6,
                                pagesize=A4,
                                encoding="utf-8",
                                fontName='DejaVuSerif')

        #style settings

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='TableHeader', fontName='DejaVuSerif', fontSize = 7.5))
        styles.add(ParagraphStyle(name='TableCell', fontName='DejaVuSerif', fontSize=7.2, spaceBefore=6, spaceAfter=6))
        styles.add(ParagraphStyle(name='TableCellB', fontName='DejaVuSerifB', fontSize=7.2))

        # Our container for 'Flowable' objects
        elements = []
        selectedSzamlatorzs = get_object_or_404(SzamlaTorzs, szamlaszam=vszamlaszam)
        selectedVevo = get_object_or_404(Vevo, pk=selectedSzamlatorzs.vevo_fk_id)
        selectedCeg = Ceg.objects.get(aktualis=True)
        tetels = SzamlaTetel.objects.filter(szamlatorzs_id=selectedSzamlatorzs.id)

        # Draw things on the PDF. Here's where the PDF generation happens.

        #Draw title
        title = Drawing(20, 20)
        title.add(Rect(self.width/2, 1, 80, 20, fillColor=colors.gray))
        title.add(String(self.width/2+10,10, 'SZÁMLA', fontSize=13,fontName='DejaVuSerif', fillColor=colors.black))
        elements.append(title)

        #draw a line after title
        lineBeforeCustomer = Drawing(self.width, 2)
        lineBeforeCustomer.add(Line(0,0, self.width, 2))
        elements.append(lineBeforeCustomer)

        #Add customer data
        #Add logo
        #elements.append(Image('raktarweb/static/images/raktar.png', hAlign= 'LEFT'))
        elements.append(Image(selectedCeg.logo, hAlign= 'LEFT'))

        #Add ceg data
        cegcim = repr(selectedCeg.iranyitoszam) + ', ' + selectedCeg.varos + ', ' + selectedCeg.utcaHazszam
        cegadoszam = 'adószám: ' + selectedCeg.adoszam
        cegbankszamlaszam = 'bankszámla: ' + selectedCeg.bankszamlaszam
        cegemail = 'email: ' + selectedCeg.emailcim
        cegweblap = 'weblap: '+ selectedCeg.weblap

        #Add vevo data
        iranyitoszam = repr(selectedVevo.iranyitoszam)
        vevocim = iranyitoszam + ', ' + selectedVevo.varos + ', ' + selectedVevo.utcaHazszam
        vevorendszam = 'Gépjármű rendszáma:   ' + selectedSzamlatorzs.rendszam
        vevogyartmany = 'Gépjármű gyártmánya:   ' + selectedSzamlatorzs.gyartmany
        vevogepjarmutipus = 'Gépjármű tipusa:   ' + selectedSzamlatorzs.gepjarmutipus
        vevogepjarmufajta = 'Gépjarmű fajtája:   ' + selectedSzamlatorzs.gepjarmufajta
        vevogepjarmukmh = 'Gépjarmű km óra:   ' + selectedSzamlatorzs.gepjarmukmh


        ceg = [
               [Paragraph("<b>Szolgáltató:</b>", styles['TableHeader'])],
               [Paragraph(selectedCeg.nev, styles['TableCellB'])],
               [Paragraph(cegcim, styles['TableCell'])],
               [Paragraph(cegadoszam, styles['TableCell'])],
               [Paragraph(cegbankszamlaszam, styles['TableCell'])],
               [Paragraph(cegemail, styles['TableCell'])],
               [Paragraph(cegweblap, styles['TableCell'])],
               ['']]

        megrendelo = [
                     [Paragraph("<b>Megrendelő:</b>", styles['TableHeader'])],
                     [Paragraph('{}'.format(selectedVevo.nev), styles['TableCellB'])],
                     [Paragraph('{}'.format(vevocim), styles['TableCell'])],
                     [Paragraph('{}'.format(vevorendszam), styles['TableCell'])],
                     [Paragraph('{}'.format(vevogyartmany), styles['TableCell'])],
                     [Paragraph('{}'.format(vevogepjarmutipus), styles['TableCell'])],
                     [Paragraph('{}'.format(vevogepjarmufajta), styles['TableCell'])],
                     [Paragraph('{}'.format(vevogepjarmukmh), styles['TableCell'])]
                     ]

        #TO DO: filter the null values from megrendelo
        cegtable = Table(ceg, colWidths=[doc.width/2.0])
        megrendelotable = Table(megrendelo, colWidths=[doc.width/2.0])
        data = [[cegtable, megrendelotable]]
        cegtable = Table(data, colWidths=[doc.width/2.0]*2)

        cegtable.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('FONT', (0,0), (-1,-1), 'DejaVuSerif'),
                                        ('BOX', (0, 0), (-1, -1), 0.5, colors.black)]))
        elements.append(cegtable)

        #Add szamlaadatok
        szamlaadatokHeader = []
        fizetesModja = Paragraph("<b>Fizetés módja</b>", styles['TableHeader'])
        szamlaadatokHeader.append(fizetesModja)
        szamlaKelte = Paragraph("<b>Számla kelte</b>", styles['TableHeader'])
        szamlaadatokHeader.append(szamlaKelte)
        teljesitesIdopontja = Paragraph("<b>Teljesítés időpontja</b>", styles['TableHeader'])
        szamlaadatokHeader.append(teljesitesIdopontja)
        fizetesiHatarido = Paragraph("<b>Fizetési határidő</b>", styles['TableHeader'])
        szamlaadatokHeader.append(fizetesiHatarido)
        szamlaSzam = Paragraph("<b>Számlaszám</b>", styles['TableHeader'])
        szamlaadatokHeader.append(szamlaSzam)
        rendelesSzam = Paragraph("<b>Rendelésszám</b>", styles['TableHeader'])
        szamlaadatokHeader.append(rendelesSzam)

        szamlaadatokCell =[]
        szamlaadatokCell.append(Paragraph(selectedSzamlatorzs.fizetesimod, styles['TableCell']))
        szamlaadatokCell.append(Paragraph(selectedSzamlatorzs.szamlakelte.date().isoformat(), styles['TableCell']))
        szamlaadatokCell.append(Paragraph(selectedSzamlatorzs.teljesitesidopontja.date().isoformat(), styles['TableCell']))
        szamlaadatokCell.append(Paragraph(selectedSzamlatorzs.fizetesihatarido.date().isoformat(), styles['TableCell']))
        szamlaadatokCell.append(Paragraph(selectedSzamlatorzs.szamlaszam, styles['TableCell']))
        szamlaadatokCell.append(Paragraph(selectedSzamlatorzs.rendelesszam, styles['TableCell']))

        szamlaadatok = [szamlaadatokHeader,szamlaadatokCell]

        szamlaadatoktable = Table(szamlaadatok, colWidths=[doc.width/6.0]*6)
        szamlaadatoktable.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                                  ('FONT', (0,0), (-1,-1), 'DejaVuSerif'),
                                                  ('BOX', (0, 0), (-1, -1), 0.5, colors.black)]))
        elements.append(szamlaadatoktable)

        #Adds line after szamlaadatok
        lineAfterSzamlaAdatok = Drawing(self.width, 2)
        lineAfterSzamlaAdatok.add(Line(0,0, self.width, 2))
        elements.append(lineAfterSzamlaAdatok)

        #Add tetelekheading
        tetelek_heading_adatok = [["VTSZ-SZJ", "Megnevezés","Me",
                         "Egységár", "K%", "Kedv", "Nettó egys", "Nettó ért", "Áfa", "Áfa é", "Bruttó é"]]

        tetelek_heading_table = Table(tetelek_heading_adatok, colWidths=[2*cm, 4*cm, 1*cm, 2*cm, 1*cm, 2*cm, 2*cm, 2*cm, 1*cm, 2*cm, 2*cm], hAlign='LEFT')
        elements.append(tetelek_heading_table)

        #Need a place to store our table rows
        tetelek_data = []
        afa_data = {}
        afa_data_list = []
        for i, tetel in enumerate(tetels):
            # Add a row to the table
            # selectedAfa = get_object_or_404(Afa, pk=tetel.afakulcs_id)
            afa = repr(tetel.afakulcs) +'%'
            mennyiseg = repr(tetel.mennyiseg) + tetel.mennyisegiegyseg
            tetelek_data.append([tetel.VTSZSZJszam, tetel.megnevezes, mennyiseg,
                                 tetel.bruttoegysegar, tetel.kedvezmenyszazalek, tetel.kedvezmenyegysegar,
                                 tetel.nettoegysegar, tetel.nettoertek, afa, tetel.afaertek, tetel.bruttoertek])
            #calculate afa summary table info
            if afa not in afa_data:
               afa_data[afa] = [tetel.nettoertek, tetel.afaertek]
            else:
               afa_data[afa][0] += tetel.nettoertek
               afa_data[afa][1] += tetel.afaertek

        for key,value in afa_data.items():
            afa_data_list.append([key,value[0], value[1]])

        # Create the table
        tetelek_table = Table(tetelek_data, colWidths=[2*cm, 4*cm, 1*cm, 2*cm, 1*cm, 2*cm, 2*cm, 2*cm, 1*cm, 2*cm, 2*cm],
                              hAlign='LEFT')
        '''
        tetelek_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                        #('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
        '''
        elements.append(tetelek_table)

        #Adds line after szamlaadatok
        lineAfterSzamlaTetelek = Drawing(self.width, 2)
        lineAfterSzamlaTetelek.add(Line(0,0, self.width, 2))
        elements.append(lineAfterSzamlaTetelek)

        #Add afa table heading
        afa_table_heading_data = [["ÁFA kulcs", "ÁFA alap","ÁFA érték"]]

        afa_table_heading_table = Table(afa_table_heading_data, colWidths=[2*cm, 2*cm, 2*cm], hAlign='RIGHT')
        elements.append(afa_table_heading_table)

        #Add Afa table
        afa_data_table = Table(afa_data_list, colWidths=[2*cm, 2*cm, 2*cm],
                              hAlign='RIGHT')
        elements.append(afa_data_table)

        #Adds line after afa osszesito
        lineAfterAfaTable = Drawing(self.width, 2)
        lineAfterAfaTable.add(Line(12*cm,0, self.width, 2))
        elements.append(lineAfterAfaTable)

        #Add osszesito paragraphs
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='right', fontName='DejaVuSans', alignment=TA_RIGHT, ))
        styles.add(ParagraphStyle(name='LeftAlign', align=TA_LEFT))

        n = selectedSzamlatorzs.nettoosszesen
        nettoParagraphtext = 'Nettó érték Ősszesen: ' + repr(selectedSzamlatorzs.nettoosszesen) + ' Ft'
        nettoParagraph = Paragraph(nettoParagraphtext, styles['right'], encoding='utf8')
        elements.append(nettoParagraph)

        #styles.add(ParagraphStyle(name='RightAlign', align=TA_RIGHT))
        afaParagraphtext = 'Afa ertek osszesen: ' + repr(selectedSzamlatorzs.afaosszesen) + ' Ft'
        afaParagraph = Paragraph(afaParagraphtext, styles['right'], encoding='utf8')
        elements.append(afaParagraph)

        bruttoParagraphtext = 'Brutto ertek osszesen: ' + repr(selectedSzamlatorzs.bruttoosszesen) + ' Ft'
        bruttoParagraph = Paragraph(bruttoParagraphtext, styles['right'], encoding='utf8')
        elements.append(bruttoParagraph)

        #Adds line after afa osszesito
        lineAfterOsszesito = Drawing(self.width, 2)
        lineAfterOsszesito.add(Line(0,0, self.width, 2))
        elements.append(lineAfterOsszesito)

        #Adds vegosszeg paragraph
        vegosszegParagraphtext = 'Fizetve(kerekites utan:' + \
                                 repr(selectedSzamlatorzs.vegosszegkerekitve) + '.- Ft'
        vegosszegkerekitveParagraph = Paragraph(vegosszegParagraphtext, styles['LeftAlign'], encoding='utf8')
        elements.append(vegosszegkerekitveParagraph)

        #Adds vegosszeg betuvel
        vegosszegbetuvelParagraphtext = 'azaz: ' + selectedSzamlatorzs.vegosszegbetuvel + ' Ft'
        vegosszegbetuvelParagraph = Paragraph(vegosszegbetuvelParagraphtext, styles['right'], encoding='utf8')
        elements.append(vegosszegbetuvelParagraph)

        # Adds megjegyzesek
        megjegyzesekParagraphtext = selectedSzamlatorzs.megjegyzesek
        megjegyzesekParagraph = Paragraph(megjegyzesekParagraphtext, styles['right'], encoding='utf8')
        elements.append(megjegyzesekParagraph)

        # Adds empthy lines before kiallito
        elements.append(Spacer(1,20))

        # Adds kiallito
        kiallitoParagraphtext = 'Kiallitó:'
        kiallitoParagraph = Paragraph(kiallitoParagraphtext, styles['LeftAlign'], encoding='utf8')
        elements.append(kiallitoParagraph)
        '''
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
        '''
        #for peldany in ['31 Eredeti peldany','32 Konyveles peldanya', '33 Vevonyilvantartas peldanya']:
        #peldany = '31 Eredeti peldany'

        doc.build(elements, onFirstPage = partial(self._header_footer, custom_footer=self.peldany),
                            onLaterPages=partial(self._header_footer, custom_footer=self.peldany),
                            canvasmaker=NumberedCanvas)

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf