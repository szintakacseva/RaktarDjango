import datetime

import django
from django.contrib.auth.models import User
from django.db import models
from django.http import request


class VTSZSZJ(models.Model):
    VTSZSZJ_szam = models.CharField("VTSZ/SZJ szám", max_length=60)

    def __str__(self):
        return self.VTSZSZJ_szam

class MennyisegiEgyseg(models.Model):
    me_megnevezes = models.CharField("Mennyiségi egység:", max_length=20)

    def __str__(self):
        return self.me_megnevezes

class Afa(models.Model):
    afakulcs = models.PositiveSmallIntegerField("Áfakulcs")

    def __str__(self):
        return str(self.afakulcs)


class Megjegyzes(models.Model):
    megjegyzesnev = models.CharField("Megjegyzés:", max_length=200)
    aktualis = models.BooleanField("Aktuális megjegyzés", default=True)

    def __str__(self):
        return self.megjegyzesnev


class Vevo(models.Model):
    nev = models.CharField("Név", max_length=100)
    adoszam = models.CharField("Adószám", max_length=20, blank=True)
    bankszamlaszam = models.CharField("Bankszámlaszám", max_length=20, blank=True)
    varos = models.CharField("Város", max_length=50, default='Budapest')
    iranyitoszam = models.PositiveSmallIntegerField("Irányítószám")
    utcaHazszam = models.CharField("Utca, házszám", max_length=100)
    orszag = models.CharField("Ország", max_length=100, default='Magyarország')
    kapcsolattarto = models.CharField("Kapcsolattartó", max_length=100, blank=True)
    emailcim = models.EmailField("Email", max_length=50, blank=True)
    telefonszam = models.CharField("Telefonszám", max_length=20, blank=True)

    def __str__(self):
        return self.nev


class Ceg(models.Model):
    nev = models.CharField("Cégnév", max_length=100)
    logo = models.ImageField("Logo", blank=True)
    adoszam = models.CharField("Adószám", max_length=20, blank=True)
    bankszamlaszam = models.CharField("Bankszámlaszám", max_length=35, blank=True)
    varos = models.CharField("Város", max_length=50, default='Budapest')
    iranyitoszam = models.PositiveSmallIntegerField("Irányítószám")
    utcaHazszam = models.CharField("Utca, házszám", max_length=100)
    orszag = models.CharField("Ország", max_length=100, default='Magyarország')
    vezeto = models.CharField("Vezető", max_length=100, blank=True)
    telefonszam = models.CharField("Telefonszám", max_length=20, blank=True)
    emailcim = models.EmailField("Email", max_length=50, blank=True)
    weblap = models.URLField("Weblap", blank=True)
    aktualis = models.BooleanField("Aktuális", default=True)

    def __str__(self):
        return self.nev


class RaktarElem(models.Model):
    RAKTARELEM_TIPUS = (
        ('Szolgáltatás', 'Szolgáltatás'),
        ('Cikk', 'Cikk'),
    )
    ARJELZES_TIPUS = (
        ('Ft', 'Forint'),
        ('USD', 'USA Dollár'),
        ('EUR', 'Euro'),
        ('GBR', 'Angol Font'),
    )
    tipus = models.CharField("Tipus", max_length=15, choices=RAKTARELEM_TIPUS)
    tetelszam = models.CharField("Tételszám", max_length=15)
    megnevezes = models.CharField("Termék megnevezése", max_length=150)
    arjelzes = models.CharField("Árjelzés", max_length=6, choices=ARJELZES_TIPUS)
    bruttoar = models.DecimalField("Bruttó ár", default=0, max_digits=6, decimal_places=0)
    nettoar = models.DecimalField("Nettó ár", default=0, blank=True, max_digits=6, decimal_places=2)
    afakulcs = models.ForeignKey(Afa)
    mennyiseg = models.IntegerField("Mennyiség", default=0, blank=True)
    mennyisegiegyseg = models.ForeignKey(MennyisegiEgyseg)
    VTSZSZJ = models.ForeignKey(VTSZSZJ)

    # noinspection PyTypeChecker
    def save(self):
        super(RaktarElem, self).save()
        self.nettoar = self.bruttoar / (100 + self.afakulcs.afakulcs) * 100
        super(RaktarElem, self).save()

    def __str__(self):
        return self.tetelszam

class SzamlaTorzs(models.Model):
    FIZETESIMOD = (
        ('kp', 'Készpénz'),
        ('átu', 'Átutalás'),
        ('bk', 'Bankkártya'),
    )
    GEPJARMU = (
        ('szg', 'Személygépkocsi'),
        ('ktg', 'Kistehergépkocsi'),
        ('mkp', 'Motorkerékpár'),
        ('pk', 'Pótkocsi'),
        ('szg4', 'Személygépkocsi 4x4'),
    )
    SZAMLATIPUS = (
        ('sza', 'SZÁMLA'),
        ('esza', 'ELŐLEG SZÁMLA'),
        ('pfsza', 'PROFORMA SZÁMLA'),
        ('szsza', 'STORNO SZÁMLA'),
    )
    loggedinuser = models.CharField("Felhasználó: ", max_length=15, blank=True, null=True)
    szamlatipus = models.CharField("Számla tipus", max_length=25, choices=SZAMLATIPUS, default='SZÁMLA')
    szamlaszam = models.CharField("Számlaszám", max_length=25, default='0000/2015/RA', blank=False, unique=True)
    rendelesszam = models.CharField("Rendelésszám", max_length=25, default='20150101/0')
    fizetesimod = models.CharField("Fizetési mód", max_length=50, default='Készpénz', choices=FIZETESIMOD)
    szamlakelte = models.DateTimeField("Számla kelte", default=django.utils.timezone.now)
    teljesitesidopontja = models.DateTimeField("Teljesítés időpontja", default=django.utils.timezone.now)
    fizetesihatarido = models.DateTimeField("Fizetési határidő", default=django.utils.timezone.now)
    vevo_fk = models.ForeignKey(Vevo)
    rendszam = models.CharField("Gépjármű rendszáma", max_length=10, blank=True)
    gyartmany = models.CharField("Gépjármű gyártmánya", max_length=20, blank=True)
    gepjarmutipus = models.CharField("Gépjármű tipusa", max_length=20, blank=True)
    gepjarmufajta = models.CharField("Gépjármű fajtája", max_length=20, default='Személygépkocsi',choices=GEPJARMU)
    gepjarmukmh = models.CharField("Gépjármű kmh", max_length=20, blank=True)
    megjegyzesek = models.TextField("Megjegyzések", max_length=500, blank=True)
    megjegyzesegyedi = models.CharField("Egyedi megjegyzesek", max_length=150, blank=True)
    afaalap = models.DecimalField("Bruttó összesen", max_length=10, default=0, max_digits=8, decimal_places=0, blank=True)
    nettoosszesen = models.DecimalField("Nettó összesen", max_length=10, default=0, max_digits=8, decimal_places=0, blank=True)
    afaosszesen = models.DecimalField("Áfa összesen", max_length=10, default=0, max_digits=8, decimal_places=0, blank=True)
    bruttoosszesen = models.DecimalField("Bruttó összesen", max_length=10, default=0, max_digits=8, decimal_places=0, blank=True)
    vegosszegkerekitve = models.DecimalField("Kerekített végösszeg", max_length=10, default=0, max_digits=8, decimal_places=0, blank=True)
    vegosszegbetuvel = models.CharField("Azaz", max_length=200, blank=True)

    def __str__(self):
        return self.szamlaszam


class SzamlaTetel(models.Model):
    szamlatorzs = models.ForeignKey(SzamlaTorzs)
    #raktarelem = models.ForeignKey(RaktarElem)
    VTSZSZJszam = models.CharField("VTSZ/SZJ szam", max_length=20, blank=True)
    megnevezes = models.CharField("Megnevezés", max_length=150, blank=True)
    mennyiseg = models.IntegerField("Mennyiség", default=0, blank=True)
    mennyisegiegyseg = models.CharField("Mennyis.egys.", max_length=10, blank=True)
    bruttoegysegar = models.DecimalField("Bruttó egységár", default=0, max_digits=6, decimal_places=0, blank=True)
    kedvezmenyszazalek = models.IntegerField("Kedvezmény százalék", default=0, blank=True)
    kedvezmenyegysegar = models.DecimalField("Kedvezményes egységár", default=0, max_digits=8, decimal_places=2, blank=True)
    nettoegysegar = models.DecimalField("Nettó egységár", default=0, max_digits=8, decimal_places=2, blank=True)
    nettoertek = models.DecimalField("Nettó érték", default=0, max_digits=8, decimal_places=0, blank=True)
    #afakulcs = models.ForeignKey(Afa)
    afakulcs = models.IntegerField("Áfakulcs", default=27, blank=True)
    afaertek = models.DecimalField("Áfa érték", default=0, max_digits=8, decimal_places=0, blank=True)
    bruttoertek = models.DecimalField("Bruttó érték", default=0, max_digits=8, decimal_places=0, blank=True)

    def __str__(self):
        return self.megnevezes

class TempSzamlaTetel(models.Model):
    szamlaszam = models.CharField("Számlaszám", max_length=25, default='0000/2015/RA')
    #szamlatorzs = models.ForeignKey(SzamlaTorzs)
    VTSZSZJszam = models.CharField("VTSZ/SZJ szam", max_length=20, blank=True)
    megnevezes = models.CharField("Megnevezés", max_length=150, blank=True)
    mennyiseg = models.IntegerField("Mennyiség", default=0, blank=True)
    mennyisegiegyseg = models.CharField("Mennyis.egys.", max_length=10, blank=True)
    bruttoegysegar = models.DecimalField("Bruttó egységár", default=0, max_digits=8, decimal_places=0, blank=True)
    kedvezmenyszazalek = models.IntegerField("Kedvezmény százalék", default=0, blank=True)
    kedvezmenyegysegar = models.DecimalField("Kedvezményes egységár", default=0, max_digits=8, decimal_places=2, blank=True)
    nettoegysegar = models.DecimalField("Nettó egységár", default=0, max_digits=8, decimal_places=2, blank=True)
    nettoertek = models.DecimalField("Nettó érték", default=0, max_digits=8, decimal_places=0, blank=True)
    #afakulcs = models.ForeignKey(Afa)
    afakulcs = models.IntegerField("Áfakulcs", default=27, blank=True)
    afaertek = models.DecimalField("Áfa érték", default=0, max_digits=8, decimal_places=0, blank=True)
    bruttoertek = models.DecimalField("Bruttó érték", default=0, max_digits=8, decimal_places=0, blank=True)

    def __str__(self):
        return self.megnevezes

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    # These fields are optional
    usercode = models.CharField("Számlaszám kód: ", max_length=2, default='OO')
    picture = models.ImageField(upload_to='imgs', blank=True)

    def __str__(self):
        return self.user.username
