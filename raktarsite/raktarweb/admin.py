from django.contrib import admin
from raktarweb.models import Vevo, Ceg
from raktarweb.models import Megjegyzes
from raktarweb.models import VTSZSZJ
from raktarweb.models import Afa
from raktarweb.models import UserProfile
from raktarweb.models import RaktarElem
from raktarweb.models import SzamlaTetel, SzamlaTorzs, MennyisegiEgyseg

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            obj.is_staff = True
            obj.save()



class RaktarElemAdmin(admin.ModelAdmin):
    list_display = ('tetelszam','megnevezes', )
    list_filter = ['megnevezes']
    search_fields = ['tetelszam']

class VevoAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Név', {'fields': ['nev', 'adoszam', 'bankszamlaszam']}),
        ('Székhely', {'fields': ['varos', 'iranyitoszam', 'utcaHazszam']}),
        ('Elérhetőség', {'fields': ['kapcsolattarto', 'emailcim', 'telefonszam']}),
    ]
    list_display = ('nev', 'varos','iranyitoszam', 'utcaHazszam' )
    list_filter = ['nev']
    search_fields = ['nev']

class CegAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Név', {'fields': ['nev', 'logo', 'adoszam', 'bankszamlaszam']}),
        ('Székhely', {'fields': ['orszag', 'varos', 'iranyitoszam', 'utcaHazszam']}),
        ('Elérhetőség', {'fields': ['vezeto', 'telefonszam', 'emailcim', 'weblap']}),
    ]
    list_display = ('nev',)
    list_filter = ['nev']
    search_fields = ['nev']


class VTSZSZJAdmin(admin.ModelAdmin):
    fieldsets = [
        ('VTSZ-SZJ szám',               {'fields': ['VTSZSZJ_szam']}),
    ]
    list_filter = ['VTSZSZJ_szam']
    search_fields = ['VTSZSZJ_szam']

class SzamlaTetelInline(admin.TabularInline):
    model = SzamlaTetel

class SzamlaTorzsAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Számlatipus',               {'fields': ['szamlatipus']}),
        ('Számlaszám',                {'fields': ['szamlaszam']}),
        ('Vevő',                      {'fields': ['vevo_fk']}),
        ('Számlakelte',               {'fields': ['szamlakelte']}),
    ]
    inlines = [SzamlaTetelInline]
    list_display = ('szamlaszam', 'szamlakelte')
    list_filter = ['szamlaszam']
    search_fields = ['szamlaszam']

# Register your models here
admin.site.register(Vevo, VevoAdmin)
admin.site.register(Ceg, CegAdmin)
admin.site.register(VTSZSZJ, VTSZSZJAdmin)
admin.site.register(Afa)
admin.site.register(Megjegyzes)
admin.site.register(MennyisegiEgyseg)
admin.site.register(RaktarElem, RaktarElemAdmin)
admin.site.register(SzamlaTorzs, SzamlaTorzsAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

