# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-12 08:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Afa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('afakulcs', models.PositiveSmallIntegerField(verbose_name='Áfakulcs')),
            ],
        ),
        migrations.CreateModel(
            name='Ceg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=100, verbose_name='Cégnév')),
                ('logo', models.ImageField(blank=True, upload_to='', verbose_name='Logo')),
                ('adoszam', models.CharField(blank=True, max_length=20, verbose_name='Adószám')),
                ('bankszamlaszam', models.CharField(blank=True, max_length=35, verbose_name='Bankszámlaszám')),
                ('varos', models.CharField(default='Budapest', max_length=50, verbose_name='Város')),
                ('iranyitoszam', models.PositiveSmallIntegerField(verbose_name='Irányítószám')),
                ('utcaHazszam', models.CharField(max_length=100, verbose_name='Utca, házszám')),
                ('orszag', models.CharField(default='Magyarország', max_length=100, verbose_name='Ország')),
                ('vezeto', models.CharField(blank=True, max_length=100, verbose_name='Vezető')),
                ('telefonszam', models.CharField(blank=True, max_length=20, verbose_name='Telefonszám')),
                ('emailcim', models.EmailField(blank=True, max_length=50, verbose_name='Email')),
                ('weblap', models.URLField(blank=True, verbose_name='Weblap')),
                ('aktualis', models.BooleanField(default=True, verbose_name='Aktuális')),
            ],
        ),
        migrations.CreateModel(
            name='Megjegyzes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('megjegyzesnev', models.CharField(max_length=200, verbose_name='Megjegyzés:')),
                ('aktualis', models.BooleanField(default=True, verbose_name='Aktuális megjegyzés')),
            ],
        ),
        migrations.CreateModel(
            name='MennyisegiEgyseg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('me_megnevezes', models.CharField(max_length=20, verbose_name='Mennyiségi egység:')),
            ],
        ),
        migrations.CreateModel(
            name='RaktarElem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipus', models.CharField(choices=[('Szolgáltatás', 'Szolgáltatás'), ('Cikk', 'Cikk')], max_length=15, verbose_name='Tipus')),
                ('tetelszam', models.CharField(max_length=15, verbose_name='Tételszám')),
                ('megnevezes', models.CharField(max_length=150, verbose_name='Termék megnevezése')),
                ('arjelzes', models.CharField(choices=[('Ft', 'Forint'), ('USD', 'USA Dollár'), ('EUR', 'Euro'), ('GBR', 'Angol Font')], max_length=6, verbose_name='Árjelzés')),
                ('bruttoar', models.DecimalField(decimal_places=0, default=0, max_digits=6, verbose_name='Bruttó ár')),
                ('nettoar', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6, verbose_name='Nettó ár')),
                ('mennyiseg', models.IntegerField(blank=True, default=0, verbose_name='Mennyiség')),
            ],
        ),
        migrations.CreateModel(
            name='SzamlaTetel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('VTSZSZJszam', models.CharField(blank=True, max_length=20, verbose_name='VTSZ/SZJ szam')),
                ('megnevezes', models.CharField(blank=True, max_length=150, verbose_name='Megnevezés')),
                ('mennyiseg', models.IntegerField(blank=True, default=0, verbose_name='Mennyiség')),
                ('mennyisegiegyseg', models.CharField(blank=True, max_length=10, verbose_name='Mennyis.egys.')),
                ('bruttoegysegar', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=6, verbose_name='Bruttó egységár')),
                ('kedvezmenyszazalek', models.IntegerField(blank=True, default=0, verbose_name='Kedvezmény százalék')),
                ('kedvezmenyegysegar', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Kedvezményes egységár')),
                ('nettoegysegar', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Nettó egységár')),
                ('nettoertek', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, verbose_name='Nettó érték')),
                ('afakulcs', models.IntegerField(blank=True, default=27, verbose_name='Áfakulcs')),
                ('afaertek', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, verbose_name='Áfa érték')),
                ('bruttoertek', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, verbose_name='Bruttó érték')),
            ],
        ),
        migrations.CreateModel(
            name='SzamlaTorzs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loggedinuser', models.CharField(blank=True, max_length=15, null=True, verbose_name='Felhasználó: ')),
                ('szamlatipus', models.CharField(choices=[('sza', 'SZÁMLA'), ('esza', 'ELŐLEG SZÁMLA'), ('pfsza', 'PROFORMA SZÁMLA'), ('szsza', 'STORNO SZÁMLA')], default='SZÁMLA', max_length=25, verbose_name='Számla tipus')),
                ('szamlaszam', models.CharField(default='0000/2015/RA', max_length=25, unique=True, verbose_name='Számlaszám')),
                ('rendelesszam', models.CharField(default='20150101/0', max_length=25, verbose_name='Rendelésszám')),
                ('fizetesimod', models.CharField(choices=[('kp', 'Készpénz'), ('átu', 'Átutalás'), ('bk', 'Bankkártya')], default='Készpénz', max_length=50, verbose_name='Fizetési mód')),
                ('szamlakelte', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Számla kelte')),
                ('teljesitesidopontja', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Teljesítés időpontja')),
                ('fizetesihatarido', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fizetési határidő')),
                ('rendszam', models.CharField(blank=True, max_length=10, verbose_name='Gépjármű rendszáma')),
                ('gyartmany', models.CharField(blank=True, max_length=20, verbose_name='Gépjármű gyártmánya')),
                ('gepjarmutipus', models.CharField(blank=True, max_length=20, verbose_name='Gépjármű tipusa')),
                ('gepjarmufajta', models.CharField(choices=[('szg', 'Személygépkocsi'), ('ktg', 'Kistehergépkocsi'), ('mkp', 'Motorkerékpár'), ('pk', 'Pótkocsi'), ('szg4', 'Személygépkocsi 4x4')], default='Személygépkocsi', max_length=20, verbose_name='Gépjármű fajtája')),
                ('gepjarmukmh', models.CharField(blank=True, max_length=20, verbose_name='Gépjármű kmh')),
                ('megjegyzesek', models.TextField(blank=True, max_length=500, verbose_name='Megjegyzések')),
                ('megjegyzesegyedi', models.CharField(blank=True, max_length=150, verbose_name='Egyedi megjegyzesek')),
                ('afaalap', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, max_length=10, verbose_name='Bruttó összesen')),
                ('nettoosszesen', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, max_length=10, verbose_name='Nettó összesen')),
                ('afaosszesen', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, max_length=10, verbose_name='Áfa összesen')),
                ('bruttoosszesen', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, max_length=10, verbose_name='Bruttó összesen')),
                ('vegosszegkerekitve', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, max_length=10, verbose_name='Kerekített végösszeg')),
                ('vegosszegbetuvel', models.CharField(blank=True, max_length=200, verbose_name='Azaz')),
            ],
        ),
        migrations.CreateModel(
            name='TempSzamlaTetel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('szamlaszam', models.CharField(default='0000/2015/RA', max_length=25, verbose_name='Számlaszám')),
                ('VTSZSZJszam', models.CharField(blank=True, max_length=20, verbose_name='VTSZ/SZJ szam')),
                ('megnevezes', models.CharField(blank=True, max_length=150, verbose_name='Megnevezés')),
                ('mennyiseg', models.IntegerField(blank=True, default=0, verbose_name='Mennyiség')),
                ('mennyisegiegyseg', models.CharField(blank=True, max_length=10, verbose_name='Mennyis.egys.')),
                ('bruttoegysegar', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, verbose_name='Bruttó egységár')),
                ('kedvezmenyszazalek', models.IntegerField(blank=True, default=0, verbose_name='Kedvezmény százalék')),
                ('kedvezmenyegysegar', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Kedvezményes egységár')),
                ('nettoegysegar', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Nettó egységár')),
                ('nettoertek', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, verbose_name='Nettó érték')),
                ('afakulcs', models.IntegerField(blank=True, default=27, verbose_name='Áfakulcs')),
                ('afaertek', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, verbose_name='Áfa érték')),
                ('bruttoertek', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, verbose_name='Bruttó érték')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usercode', models.CharField(default='OO', max_length=2, verbose_name='Számlaszám kód: ')),
                ('picture', models.ImageField(blank=True, upload_to='imgs')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vevo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nev', models.CharField(max_length=100, verbose_name='Név')),
                ('adoszam', models.CharField(blank=True, max_length=20, verbose_name='Adószám')),
                ('bankszamlaszam', models.CharField(blank=True, max_length=20, verbose_name='Bankszámlaszám')),
                ('varos', models.CharField(default='Budapest', max_length=50, verbose_name='Város')),
                ('iranyitoszam', models.PositiveSmallIntegerField(verbose_name='Irányítószám')),
                ('utcaHazszam', models.CharField(max_length=100, verbose_name='Utca, házszám')),
                ('orszag', models.CharField(default='Magyarország', max_length=100, verbose_name='Ország')),
                ('kapcsolattarto', models.CharField(blank=True, max_length=100, verbose_name='Kapcsolattartó')),
                ('emailcim', models.EmailField(blank=True, max_length=50, verbose_name='Email')),
                ('telefonszam', models.CharField(blank=True, max_length=20, verbose_name='Telefonszám')),
            ],
        ),
        migrations.CreateModel(
            name='VTSZSZJ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('VTSZSZJ_szam', models.CharField(max_length=60, verbose_name='VTSZ/SZJ szám')),
            ],
        ),
        migrations.AddField(
            model_name='szamlatorzs',
            name='vevo_fk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raktarweb.Vevo'),
        ),
        migrations.AddField(
            model_name='szamlatetel',
            name='szamlatorzs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raktarweb.SzamlaTorzs'),
        ),
        migrations.AddField(
            model_name='raktarelem',
            name='VTSZSZJ',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raktarweb.VTSZSZJ'),
        ),
        migrations.AddField(
            model_name='raktarelem',
            name='afakulcs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raktarweb.Afa'),
        ),
        migrations.AddField(
            model_name='raktarelem',
            name='mennyisegiegyseg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raktarweb.MennyisegiEgyseg'),
        ),
    ]
