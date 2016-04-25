from Scripts.pilfile import args
from django.contrib.auth.models import User
from .models import UserProfile, SzamlaTorzs, SzamlaTetel, RaktarElem

__author__ = 'takacs'

from django import forms
from django.forms import ModelForm, CharField, Textarea, TextInput, NumberInput


class AktualisTetelForm(forms.Form):
     def __init__(self, *args, **kwargs):
        super(AktualisTetelForm, self).__init__(*args, **kwargs)
        initial = kwargs.pop('initial')
        self.tetel = initial['tetel']
        self.mennyiseg = initial['mennyiseg']
        self.menyegy = initial['menyegy']
        self.brutto = initial['brutto']
        self.kedvsz = initial['kedvsz']
        self.netto = initial['netto']
        self.afa = initial['afa']
        self.nettoertek = initial['nettoertek']
        self.afaertek = initial['afaertek']
        self.bruttoertek = initial['bruttoertek']
        self.fields['brutto'].widget.attrs['onchange'] = 'myBruttoCalculations()'
        self.fields['mennyiseg'].widget.attrs['onchange'] = 'myBruttoCalculations()'
        self.fields['kedvsz'].widget.attrs['onchange'] = 'myBruttoCalculations()'
        self.fields['tetel'].widget.attrs['style'] = "width:150px"
        self.fields['mennyiseg'].widget.attrs['style'] = "width:50px"
        self.fields['menyegy'].widget.attrs['style'] = "width:63px"
        self.fields['brutto'].widget.attrs['style'] = "width:80px"
        self.fields['kedvsz'].widget.attrs['style'] = "width:45px"
        self.fields['netto'].widget.attrs['style'] = "width:70px"
        self.fields['afa'].widget.attrs['style'] = "width:30px"
        self.fields['afa'].widget.attrs['readonly'] = "readonly"
        self.fields['nettoertek'].widget.attrs['style'] = "width:70px"
        self.fields['afaertek'].widget.attrs['style'] = "width:70px"
        self.fields['bruttoertek'].widget.attrs['style'] = "width:70px"
     tetel = forms.CharField(label='', max_length=100)
     mennyiseg = forms.IntegerField(label='', min_value=0)
     menyegy = forms.CharField(label='',max_length=25)
     brutto = forms.IntegerField(label='')
     kedvsz = forms.IntegerField(label='', min_value=0)
     netto = forms.CharField(label='')
     afa = forms.CharField(label='')
     nettoertek = forms.CharField(label='')
     afaertek = forms.CharField(label='')
     bruttoertek = forms.CharField(label='')


class RaktarElemForm(forms.ModelForm):
    class Meta:
        model = RaktarElem
        fields = ('tetelszam',)
    tetelszam = forms.ModelChoiceField(queryset=RaktarElem.objects.all())

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('usercode', 'picture',)

class SzamlaTorzsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
       super(SzamlaTorzsForm, self).__init__(*args, **kwargs)
       initial = kwargs.pop('initial')
       self.loggedinuser = initial['loggedinuser']
       self.szamlaszam = initial['szamlaszam']
    class Meta:
        model = SzamlaTorzs
        # fields = '__all__'
        exclude = ('teljesitesidopontja','fizetesihatarido','afaalap','nettoosszesen',
                 'afaosszesen', 'bruttoosszesen', 'vegosszegkerekitve',)

class SzamlaTetelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SzamlaTetelForm, self).__init__(*args, **kwargs)
        #self.fields['raktarelem'].widget.attrs['style'] = "width:150px"
        self.fields['megnevezes'].widget.attrs['style'] = "width:150px"
        self.fields['mennyiseg'].widget.attrs['style'] = "width:50px"
        self.fields['mennyisegiegyseg'].widget.attrs['style'] = "width:50px"
        self.fields['bruttoegysegar'].widget.attrs['style'] = "width:100px"
        self.fields['kedvezmenyszazalek'].widget.attrs['style'] = "width:50px"
        self.fields['kedvezmenyegysegar'].widget.attrs['style'] = "width:100px"
        self.fields['afakulcs'].widget.attrs['style'] = "width:50px"
        self.fields['bruttoertek'].widget.attrs['style'] = "width:100px"

    class Meta:
        model = SzamlaTetel
        exclude = ('szamlatorzs','VTSZSZJszam',)
        widgets = {
            'megnevezes': TextInput(attrs={'size': '150'}),
            'mennyiseg': NumberInput(attrs={'size': '50'}),
            'mennyisegiegyseg': TextInput(attrs={'size': '50'}),
            'bruttoegysegar': NumberInput(attrs={'size': '100'}),
            'kedvezmenyszazalek': NumberInput(attrs={'size': '50'}),
            'kedvezmenyegysegar': NumberInput(attrs={'size': '100',}),
            'afakulcs': NumberInput(attrs={'size': '50',}),
            'bruttoertek': NumberInput(attrs={'size': '100',}),
            #'bruttoertek': NumberInput(attrs={'size': '100', 'readonly':'readonly'}),
        }

class SzamlaszamSelectForm(forms.ModelForm):
    class Meta:
        model = SzamlaTorzs
        fields = ('szamlaszam',)
    szamlaszam = forms.ModelChoiceField(queryset=SzamlaTorzs.objects.all())

class SzamlaTorzsDetailForm(forms.ModelForm):
    class Meta:
        model = SzamlaTorzs
        # fields = '__all__'
        exclude = ('teljesitesidopontja','fizetesihatarido','afaalap','nettoosszesen',
                 'afaosszesen', 'bruttoosszesen', 'vegosszegkerekitve','vegosszegbetuvel', 'megjegyzesek',
                 'megjegyzesegyedi')
        widgets = {
            'szamlatipus': TextInput(attrs={'size': '25', 'readonly':'readonly'}),
            'szamlaszam': TextInput(attrs={'size': '25', 'readonly':'readonly'}),
            'rendelesszam': TextInput(attrs={'size': '25', 'readonly':'readonly'}),
            'fizetesimod': NumberInput(attrs={'size': '50', 'readonly':'readonly'}),
            'szamlakelte':TextInput(attrs={'size': '50', 'readonly':'readonly'}),
            # TO DO :: make it vevo read only
            'vevo': TextInput(attrs={'size': '100', 'readonly':'readonly'}),
            'rendszam': TextInput(attrs={'size': '10', 'readonly':'readonly'}),
            'gyartmany': TextInput(attrs={'size': '20', 'readonly':'readonly'}),
            'gepjarmutipus': TextInput(attrs={'size': '20', 'readonly':'readonly'}),
            'gepjarmufajta': TextInput(attrs={'size': '20', 'readonly':'readonly'}),
            'gepjarmukmh': TextInput(attrs={'size': '20', 'readonly':'readonly'}),

        }