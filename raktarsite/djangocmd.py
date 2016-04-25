# -*- coding: utf-8 -*-
import datetime
import os

from django.db.models import F
from django.db.models.expressions import RawSQL
from django.http import request
from raktarweb.models import User, UserProfile, Ceg, SzamlaTorzs, Megjegyzes, RaktarElem, SzamlaTetel, TempSzamlaTetel
from raktarweb.forms import RaktarElemForm

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom
import datetime
from django.views.static import serve

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")



print ("Vallllllllllllllllll")

# one-to-one relationship
u = User.objects.get(username='rapai')
u.userprofile.usercode
u.username
print(u.username)

selectedCeg = Ceg.objects.get(aktualis=True)
print(selectedCeg.nev)

coord = {'latitude': '37.24N', 'longitude': '-115.81W'}
szamlaszam = 'Coordinates: {latitude}, {longitude}'.format(**coord)

szsz = SzamlaTorzs.objects.filter(szamlaszam__endswith=u.userprofile.usercode).count()
sorszam = 1000+szsz+1
today = datetime.date.today().year
ujszamlaszam = str(sorszam)+ '/'+str(today)+ '/'+ u.userprofile.usercode
# str(sorszam) + '/'+today+'/'+u.userprofile.usercode
#print(sorszam)
print(today)
#print(ujszamlaszam)

def generate_ujszamlaszam(**kwargs):
    # error handling - verify if the username has valid usercode
    u = User.objects.get(username='rapai')
    szsz = SzamlaTorzs.objects.filter(szamlaszam__endswith=u.userprofile.usercode).count()
    sorszam = 1000+szsz+1
    today = datetime.date.today().year
    ujszamlaszam = str(sorszam)+ '/'+str(today)+ '/'+ u.userprofile.usercode
    return ujszamlaszam

megjegyzesek = Megjegyzes.objects.filter(aktualis=True)
ujmegjegyzesek = list(megjegyzesek)
ujabb = ujmegjegyzesek.extend('VALAMI')

# print (ujabb)

def aktualis_megjegyzesek():
    megjegyzesek = Megjegyzes.objects.filter(aktualis=True)
    megjegyzesek_lista = megjegyzesek.values_list('megjegyzesnev', flat=True)
    megjegyzesek_string = ".".join(str(v) for v in megjegyzesek_lista)
    return str(megjegyzesek_string)

megjegyzesek = Megjegyzes.objects.filter(aktualis=True)
megjegyzesek_lista = megjegyzesek.values_list('megjegyzesnev', flat=True)
megjegyzesek_string = ".".join(str(v) for v in megjegyzesek_lista)

# print(aktualis_megjegyzesek())
'''
netto_osszesen = 900

netto_osszesen += netto_osszesen

SzamlaTorzs.objects.filter(szamlaszam= '1005/2015/TA').update(afaalap=500, nettoosszesen = netto_osszesen,
                afaosszesen= 600, bruttoosszesen = 700, vegosszegkerekitve = 800 )

'''
# formset with different initial values
'''
Different initial data for each form in a Django formset
Formset = formset_factory(SomeForm, extra=len(some_objects)
some_formset = FormSet(initial=[{'id': 'x.id'} for x in some_objects])
'''

'''
f = RaktarElemForm()
print(f)

q=Ceg.objects.all()
print(q)
'''
'''
to_save_tetelek = []
to_print_tetelek = {}


if bool(1):
  tetel = SzamlaTetel(
  szamlatorzs_id = 55,
  VTSZSZJszam = "45678-12",
  megnevezes = "kovacs",
  mennyiseg = 3,
  mennyisegiegyseg = "db",
  bruttoegysegar = 8888,
  kedvezmenyszazalek = 10,
  kedvezmenyegysegar = 8000,
  nettoegysegar = 6400,
  nettoertek = 21000,
  afakulcs = 27,
  afaertek = 3000,
  bruttoertek = 24500);
  to_save_tetelek.append(tetel)

if bool(1):
  for tetel in to_save_tetelek:
    print(repr(tetel.megnevezes))
    tetel.save()

tetelek[egyedi_id] = [szamlatorzs_id, VTSZSZJszam, megnevezes, mennyiseg, mennyisegiegyseg, bruttoegysegar,
                             kedvezmenyszazalek, kedvezmenyegysegar, nettoegysegar, nettoertek, afakulcs, afaertek,
                             bruttoertek]
for x in seq:
    o = SomeObject()
    o.foo = x
    o.save()

becomes

l = []
for x in seq:
    o = SomeObject()
    o.foo = x
    l.append(o)
insert_many(l)

afa_data = {}
eredmeny_list = []
afaertek = 500
ujafaertek = 1000
afaalap = 300
ujafaalap = 600

for afakulcs in ['25%', '10%', '25%']:
    if afakulcs not in afa_data:
       afa_data[afakulcs] = [afaalap, afaertek]
    else:
       afa_data[afakulcs][0] += ujafaalap
       afa_data[afakulcs][1] += ujafaertek

for key,value in afa_data.items():
    eredmeny_list.append([key,value[0], value[1]])


print(afa_data.items())
print (repr(eredmeny_list))
'''

'''
def plisting(request):
    if 'plist' not in request.session:
        request.session['plist']=[]
    plist = request.session['plist']
    if 'entry' in request.POST:
        entry = str(request.POST['entry'])
        key = str(request.POST['key'])
        plist = plist+[[entry,key]]
    request.session['plist'] = plist
    return render(request,'evaluator/plisting.html',{'plist':plist})

szamla_tetelek = SzamlaTetel.objects.select_for_update().filter(szamlatorzs_id=55)
print (repr(szamla_tetelek))

for tetel in szamla_tetelek:
        tetel.update(bruttoegysegar = -tetel.bruttoegysegar,
                                 kedvezmenyegysegar = -tetel.kedvezmenyegysegar,
                                 nettoegysegar = -tetel.nettoegysegar,
                                 nettoertek = -tetel.nettoertek,
                                 afaertek = - tetel.afaertek,
                                 bruttoertek = -tetel.bruttoertek)
'''
'''
SzamlaTetel.objects.select_for_update().filter(szamlatorzs_id=55).update(bruttoegysegar = F('bruttoegysegar')*(-1),
                                 kedvezmenyegysegar = 6000,
                                 nettoegysegar = 6000,
                                 nettoertek = 6000,
                                 afaertek = 6000,
                                 bruttoertek = 6000)

'''
szamlakList = SzamlaTorzs.objects.filter()
szamlakList.annotate(val=RawSQL("select szamlaszam from raktarweb_szamlatorzs where szamlaszam between %s and %s",
                                            ('1041', '1056', )))


def create_xml(l_szamlak):
    if 'l_szamlak':
        szamlak = Element('szamlak')
        comment = Comment('23_2014 szamlasema alapján')
        szamlak.append(comment)
        export_datuma = SubElement(szamlak, "export_datuma")
        export_datuma.text = str(datetime.date.today())
        ElementTree.ElementTree(szamlak).write("adatexport.xml", encoding="UTF-8",xml_declaration=True)
    else:
        print ("Nincsennek számlák")
    return prettify(szamlak)

#print(create_xml(szamlakList))
#ElementTree.ElementTree(create_xml(szamlak)).write("adatexport.xml")
#xmlFile = open('raktarweb/adatexport.xml', 'r')
#print(xmlFile)

def downloadFile():
    filepath = 'e:/Temp/adatexport.xml'
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))

#downloadFile

def deletetempszamlatetel(v_szamlaszam):
    TempSzamlaTetel.objects.filter(szamlaszam=v_szamlaszam).delete()

deletetempszamlatetel('1060/2016/TA')



# import django
# django.setup()

# exec(open(filename).read())
# exec(open('djangocmd.py').read())