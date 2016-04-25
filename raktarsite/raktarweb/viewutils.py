import datetime
from xml.etree.ElementTree import Element, SubElement, Comment, XML
from xml.etree import ElementTree
from xml.dom import minidom

from .forms import SzamlaTorzsForm, RaktarElemForm
from .models import SzamlaTetel, TempSzamlaTetel

from django.http import request, HttpResponse

__author__ = 'takacs'

from .models import SzamlaTorzs, User, Megjegyzes

def generate_ujszamlaszam(vuser):
    # error handling - verify if the username has valid usercode
    u = User.objects.get(username=vuser)
    szsz = SzamlaTorzs.objects.filter(szamlaszam__endswith=u.userprofile.usercode).count()
    sorszam = 1000+szsz+1
    today = datetime.date.today().year
    ujszamlaszam = str(sorszam)+ '/'+str(today)+ '/'+ u.userprofile.usercode
    return ujszamlaszam

def aktualis_megjegyzesek():
    # error handling - verify if theere are megjegyzes objects in the database
    megjegyzesek = Megjegyzes.objects.filter(aktualis=True)
    megjegyzesek_lista = megjegyzesek.values_list('megjegyzesnev', flat=True)
    megjegyzesek_string = ".".join(str(v) for v in megjegyzesek_lista)
    return str(megjegyzesek_string)

def plisting(request):
    if 'plist' not in request.session:
        request.session['plist']=[]
    plist = request.session['plist']
    if 'entry' in request.POST:
        entry = str(request.POST['entry'])
        key = str(request.POST['key'])
        plist = plist+[[entry,key]]
    request.session['plist'] = plist
    return plist

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_xml(l_szamlak, kezdo_szamla, zaro_szamla):
    if 'l_szamlak':
        #for prefix, uri in ns.iteritems():
        ElementTree.register_namespace("szam", "http://schemas.nav.gov.hu/2013/szamla")
        root = Element("{http://schemas.nav.gov.hu/2013/szamla}szamlak")
        comment = Comment('23_2014 szamlasema alapján')
        root.append(comment)
        export_datuma = SubElement(root, "{http://schemas.nav.gov.hu/2013/szamla}export_datuma")
        export_datuma.text = str(datetime.date.today())
        export_szla_db = SubElement(root, "{http://schemas.nav.gov.hu/2013/szamla}export_szla_db")
        export_szla_db.text = str(len(list(l_szamlak)))
        kezdo_szla_szam = SubElement(root, "{http://schemas.nav.gov.hu/2013/szamla}kezdo_szla_szam")
        kezdo_szla_szam.text = kezdo_szamla
        zaro_szla_szam = SubElement(root, "{http://schemas.nav.gov.hu/2013/szamla}zaro_szla_szam")
        zaro_szla_szam.text = zaro_szamla


        for item in l_szamlak:

          szamla = SubElement(root, "{http://schemas.nav.gov.hu/2013/szamla}szamla")
          #fejlec
          fejlec = SubElement(szamla, "{http://schemas.nav.gov.hu/2013/szamla}fejlec")
          szlasorszam = SubElement(fejlec, "{http://schemas.nav.gov.hu/2013/szamla}szlasorszam")
          szlasorszam.text = item.szamlaszam
          szlatipus = SubElement(fejlec, "{http://schemas.nav.gov.hu/2013/szamla}szlatipus")
          szlatipus.text = item.szamlatipus
          szladatum = SubElement(fejlec, "{http://schemas.nav.gov.hu/2013/szamla}szladatum")
          szladatum.text = str(item.szamlakelte)
          teljdatum = SubElement(fejlec, "{http://schemas.nav.gov.hu/2013/szamla}teljdatum")
          teljdatum.text = str(item.teljesitesidopontja)
          # szamlakibocsato
          szamlakibocsato = SubElement(szamla, "{http://schemas.nav.gov.hu/2013/szamla}szamlakibocsato")
          #vevo
          vevo = SubElement(szamla, "{http://schemas.nav.gov.hu/2013/szamla}vevo")
          adoszam = SubElement(vevo, "{http://schemas.nav.gov.hu/2013/szamla}adoszam")
          adoszam.text = item.adoszam
          nev = SubElement(vevo, "{http://schemas.nav.gov.hu/2013/szamla}nev")
          nev.text = item.nev
          cim = SubElement(vevo, "{http://schemas.nav.gov.hu/2013/szamla}cim")
          iranyitoszam = SubElement(cim, "{http://schemas.nav.gov.hu/2013/szamla}iranyitoszam")
          iranyitoszam.text = str(item.iranyitoszam)
          telepules = SubElement(cim, "{http://schemas.nav.gov.hu/2013/szamla}telepules")
          telepules.text = item.varos
          kozterulet_neve = SubElement(cim, "{http://schemas.nav.gov.hu/2013/szamla}kozterulet_neve")
          kozterulet_neve.text = item.utcaHazszam

          #termekek
          termek_szolgaltatas_tetelek = SubElement(szamla, "{http://schemas.nav.gov.hu/2013/szamla}termek_szolgaltatas_tetelek")
          szamla_tetelek = SzamlaTetel.objects.filter(szamlatorzs_id=item.id)
          for tetel in szamla_tetelek:
              termeknev = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}termeknev")
              termeknev.text = tetel.megnevezes
              menny = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}menny")
              menny.text = str(tetel.mennyiseg)
              mertekegys = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}mertekegys")
              mertekegys.text = tetel.mennyisegiegyseg
              nettoar = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}nettoar")
              nettoar.text = str(tetel.nettoertek)
              nettoegysar = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}nettoegysar")
              nettoegysar.text = str(tetel.nettoegysegar)
              adokulcs = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}adokulcs")
              adokulcs.text = str(tetel.afakulcs)
              adoertek = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}adoertek")
              adoertek.text = str(tetel.afaertek)
              szazalekertek = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}szazalekertek")
              szazalekertek.text = str(tetel.kedvezmenyszazalek)
              bruttoar = SubElement(termek_szolgaltatas_tetelek, "{http://schemas.nav.gov.hu/2013/szamla}bruttoar")
              bruttoar.text = str(tetel.bruttoertek)


          osszesites = SubElement(szamla, "{http://schemas.nav.gov.hu/2013/szamla}osszesites")
          afarovat = SubElement(osszesites, "{http://schemas.nav.gov.hu/2013/szamla}afarovat")
          nettoar = SubElement(afarovat, "{http://schemas.nav.gov.hu/2013/szamla}nettoar")
          adokulcs = SubElement(afarovat, "{http://schemas.nav.gov.hu/2013/szamla}adokulcs")
          adoertek = SubElement(afarovat, "{http://schemas.nav.gov.hu/2013/szamla}adoertek")
          bruttoar = SubElement(afarovat, "{http://schemas.nav.gov.hu/2013/szamla}bruttoar")

          vegosszeg = SubElement(osszesites, "{http://schemas.nav.gov.hu/2013/szamla}vegosszeg")
          nettoarossz = SubElement(vegosszeg, "{http://schemas.nav.gov.hu/2013/szamla}nettoarossz")
          nettoarossz.text = str(item.nettoosszesen)
          afaertekossz = SubElement(vegosszeg, "{http://schemas.nav.gov.hu/2013/szamla}afaertekossz")
          afaertekossz.text = str(item.afaosszesen)
          bruttoarossz = SubElement(vegosszeg, "{http://schemas.nav.gov.hu/2013/szamla}bruttoarossz")
          bruttoarossz.text = str(item.bruttoosszesen)
          afa_tartalom = SubElement(vegosszeg, "{http://schemas.nav.gov.hu/2013/szamla}afa_tartalom ")
          afa_tartalom.text = str(item.afaalap)

        #add elements to element tree
        tree = ElementTree.ElementTree(root)
        tree.write("adatexport.xml", encoding="UTF-8",xml_declaration=True,  method="xml")

        #root = tree.getroot()
        #ElementTree.tostring(root)
        #myfile = ElementTree.tostring(root)
        #response = HttpResponse(myfile, content_type='application/xml')
        #response['Content-Disposition'] = 'attachment; filename="adat.xml"'
        #return response

    else:
        print ("Nincsennek még ilyen számlák")

def aktualisszamlakep(request, v_user, v_szamlaszam):
    szamla_torzs_form = SzamlaTorzsForm(request.POST or None,
                                        initial = {"loggedinuser": v_user,
                                                    "szamlaszam": v_szamlaszam})
    # create raktarelem form
    raktar_elem_form = RaktarElemForm(request.POST)
    # get the tetels from temporary table and add it to the aktualis tetelek table
    tetelek_list = TempSzamlaTetel.objects.filter(szamlaszam=request.session['temp_szamlaszam'])
    return szamla_torzs_form, raktar_elem_form, tetelek_list

def deletetempszamlatetel():
    #SzamlaTorzs.objects.raw('delete from raktarweb_tempszamlatetel where szamlaszam = %s', [v_szamlaszam])
    TempSzamlaTetel.objects.all().delete()