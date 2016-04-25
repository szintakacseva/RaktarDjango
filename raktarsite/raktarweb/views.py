import datetime
import decimal
import logging
import mimetypes
import os
from io import BytesIO
from wsgiref.util import FileWrapper

from django.conf.global_settings import MEDIA_ROOT
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import F
from django.forms import BaseFormSet, formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views import generic

from .forms import SzamlaTorzsForm, SzamlaTetelForm, RaktarElemForm, AktualisTetelForm, SzamlaszamSelectForm, \
    SzamlaTorzsDetailForm
from .forms import UserForm, UserProfileForm
from .models import Vevo, Afa, RaktarElem, VTSZSZJ, SzamlaTorzs, SzamlaTetel, TempSzamlaTetel
from .viewutils import generate_ujszamlaszam, aktualis_megjegyzesek, create_xml, aktualisszamlakep, deletetempszamlatetel
from .printing import MyPrint

# Get an instance of a logger
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'raktarweb/index.html')

def thanks(request):
    return render(request, 'raktarweb/thanks.html')

def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
        'raktarweb/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
        context)


def save_file(file, path=''):
    filename = file._get_name()
    fd = open('%s/%s' % (MEDIA_ROOT, str(path) + str(filename)), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()


def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/raktarweb/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Raktarweb account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('raktarweb/login.html', {}, context)

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/raktarweb/')


@login_required
def raktar(request):
    context = {}
    return render(request, 'raktarweb/raktar.html', context)

@login_required
def printinvoice(request, peldany):
    # Create the HttpResponse object with the appropriate PDF headers.
    #szamlaszam = '1008/2015/TA'
    szamlaszam = request.session['temp_szamlaszam']
    szamlanev = "Szamla_"+szamlaszam+".pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Invoice.pdf"'
    #TO DO:: to set arbitrary file name
    #response['Content-Disposition'] = 'attachment; filename="%s" % (szamlanev)'
    #"%s%s" % (self.rank, self.suit)
    buffer = BytesIO()
    report = MyPrint(buffer, 'A4', peldany)
    pdf = report.print_invoice(szamlaszam)
    response.write(pdf)
    return response

def sikeres(request):
    '''
    if request.method == 'POST':  # If the form has been submitted..
        if 'btn_generalas' in request.POST:
         return HttpResponseRedirect('raktarweb/pdf.html')
         #return HttpResponseRedirect('raktarweb/sikeres.html')
    else:
    '''
    return render_to_response('raktarweb/sikeres.html')

'''
@login_required
def pdf(request):
    # get the current szamlaszam from session
    szamlaszam = request.session['temp_szamlaszam']
    invoice_name = "szamla" + szamlaszam + ".pdf"

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    buffer = BytesIO()
    report = MyPrint(buffer, 'A4')
    pdf = report.print_invoice(szamlaszam)
    response.write(pdf)
    return response
'''

def jsonexample(request):
    response = JsonResponse({'foo': 'bar'})
    response.content
    return response

@login_required
def ujszamla(request):
    # removes all the elements from the temp tetelek table
    if request.method == 'POST':  # If the form has been submitted...
        # TO DO - error message to verify if the user has userprofile
        request.session['temp_szamlaszam'] = generate_ujszamlaszam(request.user)
        szamla_torzs_form, raktar_elem_form,  tetelek_list = aktualisszamlakep(request, request.user, request.session['temp_szamlaszam'])

        if 'btn_vevoadatok' in request.POST:
            vevo_id = request.POST.get('vevo_fk', '')
            try:
               selected_vevo = get_object_or_404(Vevo, pk=vevo_id)
            except (ValueError, Vevo.DoesNotExist):
               return render(request, 'raktarweb/ujszamla.html', {
                'szamla_torzs_form': szamla_torzs_form,
                'raktar_elem_form': raktar_elem_form,
                'tetelek_list': tetelek_list,
                'error_message_vevo': "Nem választott ki vevőt!!!!!!",
                })

            else:
              cim = repr(selected_vevo.iranyitoszam) + ", " + selected_vevo.varos + ", " + selected_vevo.utcaHazszam
              adoszam = selected_vevo.adoszam
              szamla_torzs_form, raktar_elem_form,  tetelek_list = aktualisszamlakep(request, request.user, request.session['temp_szamlaszam'])
              return render(request, 'raktarweb/ujszamla.html', {
                'szamla_torzs_form': szamla_torzs_form,
                'raktar_elem_form': raktar_elem_form,
                'cim': cim,
                'adoszam': adoszam,
                'tetelek_list': tetelek_list,})

        if 'btn_aktualis_tetel_kereses' in request.POST:
            szamla_torzs_form, raktar_elem_form,  tetelek_list = aktualisszamlakep(request, request.user, request.session['temp_szamlaszam'])
            selected_tetelszam = request.POST.get('tetelszam', '')

            try:
              selected_re = get_object_or_404(RaktarElem, pk=selected_tetelszam)

            except (ValueError, RaktarElem.DoesNotExist):
              return render(request, 'raktarweb/ujszamla.html', {
                 'szamla_torzs_form': szamla_torzs_form,
                 'raktar_elem_form': raktar_elem_form,
                 'tetelek_list': tetelek_list,
                 'error_message_raktar_elem': "Nincs kiválasztva raktarelem!!!!"
                 })
            else:
                 #note:: not put in try because of the foreign key constraint on Afa
                 selectedAfa = get_object_or_404(Afa, pk=selected_re.afakulcs_id)
                 szamla_torzs_form, raktar_elem_form,  tetelek_list = aktualisszamlakep(request, request.user, request.session['temp_szamlaszam'])
                 aktualis_tetel_form = AktualisTetelForm( initial = {"tetel": selected_re.megnevezes,
                                                                "mennyiseg": 1,
                                                                "menyegy": 'db',
                                                                "brutto": selected_re.bruttoar,
                                                                "kedvsz": 0,
                                                                "netto": selected_re.nettoar,
                                                                "afa": selectedAfa.afakulcs,
                                                                "nettoertek":0,
                                                                "afaertek":0,
                                                                "bruttoertek":0,})

                 return render(request, 'raktarweb/ujszamla.html', {
                        'szamla_torzs_form': szamla_torzs_form,
                        'raktar_elem_form': raktar_elem_form,
                        'aktualis_tetel_form': aktualis_tetel_form,
                        'tetelek_list': tetelek_list,
                        #'proba': selected_re.afakulcs
                   })

        if 'btn_add_tetel' in request.POST:
            szamla_torzs_form, raktar_elem_form,  tetelek_list = aktualisszamlakep(request, request.user, request.session['temp_szamlaszam'])
            selected_tetelszam = request.POST.get('tetelszam', '')
            try:
              selected_re = get_object_or_404(RaktarElem, pk=selected_tetelszam)
            except (ValueError, RaktarElem.DoesNotExist):
               return render(request, 'raktarweb/ujszamla.html', {
                 'szamla_torzs_form': szamla_torzs_form,
                 'raktar_elem_form': raktar_elem_form,
                 'tetelek_list': tetelek_list,
                 'error_message_aktualizalas': "Nincs kiválasztva raktarelem. Előbb válasszon, majd aktualizálja!!!"
                 })
            else:
              # note:: no check because of the foreign key constraint
              #TO DO :: error message to the user if selected a tetel
              selected_VTSZSZJ = get_object_or_404(VTSZSZJ, pk=selected_re.VTSZSZJ_id)
              tetel = request.POST.get('tetel', '')
              mennyiseg = request.POST.get('mennyiseg', '')
              menyegy = request.POST.get('menyegy', '')
              brutto = decimal.Decimal(request.POST.get('brutto', ''))
              kedvsz = request.POST.get('kedvsz', '')
              #TO DO :: error message if Decimal is missing :: exception type InvalidOperation
              netto = decimal.Decimal(request.POST.get('netto', ''))
              afa = request.POST.get('afa', '')
              bruttoertek = decimal.Decimal(request.POST.get('bruttoertek', ''))
              afaertek = decimal.Decimal(request.POST.get('afaertek', ''))
              nettoertek = decimal.Decimal(request.POST.get('nettoertek', ''))
              # setting the SzamlaTetel object
              # creating a global table with already existing elements
              # TO DO :: this approach should be replaced with a better alternative(sessions or json)
              # saved the tetels in a temporary database table
              tetel = TempSzamlaTetel(
                  szamlaszam = request.session['temp_szamlaszam'],
                  VTSZSZJszam = selected_VTSZSZJ.VTSZSZJ_szam,
                  megnevezes = tetel,
                  mennyiseg = mennyiseg,
                  mennyisegiegyseg = menyegy,
                  bruttoegysegar = brutto,
                  kedvezmenyszazalek = kedvsz,
                  kedvezmenyegysegar = 0,
                  nettoegysegar = netto,
                  nettoertek = nettoertek,
                  afakulcs = afa,
                  afaertek = afaertek,
                  bruttoertek = bruttoertek)
              # to_save_tetelek.append(tetel)
              # request.session['temp_tetelek'] = to_save_tetelek
              # TO DO :: verify if the aktuális tétel is filled with values, otherwise error
              tetel.save()

              # get the tetels from temporary table and add it to the aktualis tetelek table
              # TO DO error message
              szamla_torzs_form, raktar_elem_form,  tetelek_list = aktualisszamlakep(request, request.user, request.session['temp_szamlaszam'])
              return render(request, 'raktarweb/ujszamla.html', {
                'szamla_torzs_form': szamla_torzs_form,
                'raktar_elem_form': raktar_elem_form,
                'tetelek_list':tetelek_list,
                #'proba': tetelek_list[0].megnevezes,
                 })

        if 'btn_SavePdf' in request.POST:
            # valtozo = request.session['temp_tetelek'][0].megnevezes
            if szamla_torzs_form.is_valid():
                netto_osszesen = 0
                afa_osszesen = 0
                brutto_osszesen = 0
                szamla_torzs = szamla_torzs_form.save(commit=False)
                szamla_torzs.szamlakelte = datetime.date.today()  # to be formatted
                szamla_torzs.teljesitesidopontja = datetime.date.today()
                szamla_torzs.fizetesihatarido = datetime.date.today()
                szamla_torzs.megjegyzesek = aktualis_megjegyzesek()

                szamla_torzs.save()
                request.session['temp_szamlaszam'] = szamla_torzs.szamlaszam
                #request.session['temp_szamlatorzs_id'] = szamla_torzs.id
                #here to save szamla tételek, update szamlatorzs_id
                temp_tetelek = TempSzamlaTetel.objects.filter(szamlaszam=request.session['temp_szamlaszam'])
                to_save_tetelek = temp_tetelek
                for temp_tetel in temp_tetelek:
                    tetel = SzamlaTetel()
                    tetel.szamlatorzs_id = szamla_torzs.id
                    tetel.VTSZSZJszam = temp_tetel.VTSZSZJszam
                    tetel.megnevezes = temp_tetel.megnevezes
                    tetel.mennyiseg = temp_tetel.mennyiseg
                    tetel.mennyisegiegyseg = temp_tetel.mennyisegiegyseg
                    tetel.bruttoegysegar = temp_tetel.bruttoegysegar
                    tetel.kedvezmenyszazalek = temp_tetel.kedvezmenyszazalek
                    tetel.kedvezmenyegysegar = temp_tetel.kedvezmenyegysegar
                    tetel.nettoegysegar = temp_tetel.nettoegysegar
                    tetel.nettoertek = temp_tetel.nettoertek
                    tetel.afakulcs = temp_tetel.afakulcs
                    tetel.afaertek = temp_tetel.afaertek
                    tetel.bruttoertek = temp_tetel.bruttoertek
                    netto_osszesen += tetel.nettoertek
                    afa_osszesen += tetel.afaertek
                    brutto_osszesen += tetel.bruttoertek
                    request.session['temp_szamlaszam'] = szamla_torzs.szamlaszam
                    tetel.save()

                SzamlaTorzs.objects.filter(szamlaszam=request.session['temp_szamlaszam']).update(afaalap=1700, nettoosszesen = netto_osszesen,
                afaosszesen= afa_osszesen, bruttoosszesen = brutto_osszesen, vegosszegkerekitve = brutto_osszesen )

                # removes the temp tetels from temp tetelek table
                # TempSzamlaTetel.objects.all().delete()
                # Redirect to a 'success' page
                # return HttpResponseRedirect('raktarweb/pdf.html')
                #return HttpResponseRedirect('raktarweb/sikeres.html', {'your_name': 'hhhhhhhhhhhhhhh'})
                latest_szamlatorzs_list = SzamlaTorzs.objects.filter(szamlaszam=request.session['temp_szamlaszam'])
                peldany_list = [1, 2, 3]
                context = {'latest_szamlatorzs_list': latest_szamlatorzs_list, 'peldany_list': peldany_list}
                return render_to_response('raktarweb/sikeres.html', context)
            else:
                szamla_torzs_form, raktar_elem_form,  tetelek_list = aktualisszamlakep(request, request.user, request.session['temp_szamlaszam'])
                return render(request, 'raktarweb/ujszamla.html', {
                'szamla_torzs_form': szamla_torzs_form,
                'raktar_elem_form': raktar_elem_form,
                'tetelek_list':tetelek_list,
                'error_message_vevo': "Válasszon vevőt!!!!",
                 })

    else:
        szamla_torzs_form = SzamlaTorzsForm(initial = {"loggedinuser": request.user, "szamlaszam": generate_ujszamlaszam(request.user)})
        raktar_elem_form = RaktarElemForm()
        deletetempszamlatetel()

    c = {'szamla_torzs_form': szamla_torzs_form,
         'raktar_elem_form': raktar_elem_form,
         }
    c.update(csrf(request))

    return render_to_response('raktarweb/ujszamla.html', c)

@login_required
def sztornozas(request):
    latest_szamlatorzs_list = SzamlaTorzs.objects.all()
    context = {'latest_szamlatorzs_list': latest_szamlatorzs_list}
    return render(request, 'raktarweb/sztornozas.html', context)

@login_required
def detail(request, szamlatorzs_id, peldany):
    '''1.setting
    return HttpResponse("You're looking at question %s." % question_id)
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question})
    '''

    # return HttpResponse("You're looking at szamla %s." % szamlatorzs_id)
    '''
    proba = szamlatorzs_id
    szamlatorzs = get_object_or_404(SzamlaTorzs, pk=szamlatorzs_id)
    context = {'szamlatorzs': szamlatorzs}
    return render(request, 'raktarweb/detail.html', context)
    '''
    # get the current szamlaszam from session
    szamla = SzamlaTorzs.objects.get(pk=szamlatorzs_id)
    szamlafilenev = "szamla" + szamla.szamlaszam + "_" + peldany + ".pdf"

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    response['Content-Disposition'] = "attachment; filename=" + szamlafilenev
    buffer = BytesIO()
    report = MyPrint(buffer, 'A4', peldany)
    pdf = report.print_invoice(szamla.szamlaszam)
    response.write(pdf)
    return response

def results(request, szamlatorzs_id):
    response = "You're looking at the results of szamla %s."
    return HttpResponse(response % szamlatorzs_id)

def vote(request, szamlatorzs_id):
    return HttpResponse("You're voting on szamla %s." % szamlatorzs_id)

'''
class DetailView(generic.DetailView):
    model = SzamlaTorzs
    template_name = 'raktarweb/detail.html'

def vote(request, szamlatorzs_id):
    #return HttpResponse("You're voting on question %s." % question_id)
    p = get_object_or_404(SzamlaTorzs, pk=szamlatorzs_id)
    try:
        selected_tetel = p.szamlatetel_set.get(pk=request.POST['szamlatetel'])
    except (KeyError, SzamlaTetel.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'raktarweb/detail.html', {
            'szamlatorzs': p,
            'error_message': "You didn't select a szamlatorzs.",
        })
    else:
        selected_tetel.bruttoar = -1
        selected_tetel.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('raktarweb:results', args=(p.id,)))

class ResultsView(generic.DetailView):
    model = SzamlaTorzs
    template_name = 'raktarweb/results.html'

'''
@login_required
def ujsztornozas(request):

    if request.method=='POST':
            szamlaszam_select_form = SzamlaszamSelectForm()
            if 'btn_search' in request.POST:

                szamlatorzs_id = request.POST.get('szamlaszam','')
                szamlatorzs = get_object_or_404(SzamlaTorzs, pk=szamlatorzs_id)
                szamla_tetelek = SzamlaTetel.objects.filter(szamlatorzs_id=szamlatorzs_id)
                request.session['temp_szamlatorzs_id'] = szamlatorzs.id
                #TO DO :: javascript to hide/unhide the initial div
                return render(request, 'raktarweb/ujsztornozas.html', {
                 'szamlaszam_select_form': szamlaszam_select_form,
                 'szamlatorzs': szamlatorzs,
                 'tetelek_list': szamla_tetelek
                })
            if 'btn_sztorno' in request.POST:
                #temp_szamlatorzs = get_object_or_404(SzamlaTorzs, pk=request.session['temp_szamlatorzs_id'])
                #szamla_tetelek = SzamlaTetel.objects.filter(szamlatorzs_id=request.session['temp_szamlatorzs_id'])
                SzamlaTorzs.objects.filter(pk=request.session['temp_szamlatorzs_id']).update(afaalap=F('afaalap')*(-1),
                                                                     nettoosszesen =F('nettoosszesen')*(-1),
                                                                     afaosszesen=F('afaosszesen')*(-1),
                                                                     bruttoosszesen =F('bruttoosszesen')*(-1),
                                                                     vegosszegkerekitve =F('vegosszegkerekitve')*(-1),
                                                                     szamlatipus='sztornó')
                SzamlaTetel.objects.select_for_update().filter(szamlatorzs_id=request.session['temp_szamlatorzs_id']).update(
                                 bruttoegysegar = F('bruttoegysegar')*(-1),
                                 kedvezmenyegysegar = F('kedvezmenyegysegar')*(-1),
                                 nettoegysegar = F('nettoegysegar')*(-1),
                                 nettoertek = F('nettoertek')*(-1),
                                 afaertek = F('afaertek')*(-1),
                                 bruttoertek = F('bruttoertek')*(-1))

                # TO DO:: else, error message, must select szamlaszam

    #if a GET (or any other method) we'll create a blank form
    else:
        szamlaszam_select_form = SzamlaszamSelectForm()

    return render(request, 'raktarweb/ujsztornozas.html', {'szamlaszam_select_form': szamlaszam_select_form})

@login_required
def adatexport(request):

    if request.method=='POST':
            szamlaszam_select_kezdeti_form = SzamlaszamSelectForm()
            #trick to be done to have different field name in the same forms
            szamlaszam_select_kezdeti_form.fields['kezdeti'] = szamlaszam_select_kezdeti_form.fields['szamlaszam']
            del szamlaszam_select_kezdeti_form.fields['szamlaszam']
            szamlaszam_select_vegso_form = SzamlaszamSelectForm()
            szamlaszam_select_vegso_form.fields['vegso'] = szamlaszam_select_vegso_form.fields['szamlaszam']
            del szamlaszam_select_vegso_form.fields['szamlaszam']
            if 'btn_search' in request.POST:

                szamlatorzs_kezdeti_id = request.POST.get('kezdeti','')
                szamlatorzs_kezdeti = get_object_or_404(SzamlaTorzs, pk=szamlatorzs_kezdeti_id)
                szamlatorzs_vegso_id = request.POST.get('vegso','')
                szamlatorzs_vegso = get_object_or_404(SzamlaTorzs, pk=szamlatorzs_vegso_id)

                szamlakList = SzamlaTorzs.objects.raw('select * from raktarweb_szamlatorzs szt, raktarweb_vevo v '
                                                      'where szt.szamlaszam between %s and %s and szt.vevo_fk_id = v.id '
                                                      'order by szamlaszam',
                                                  [szamlatorzs_kezdeti.szamlaszam, szamlatorzs_vegso.szamlaszam])

                #szamlak = SzamlaTorzs.objects.filter()
                #Entry.objects.filter(pub_date__gt=datetime.date(2005, 1, 3), headline='Hello')
                #szamlak.annotate(val=RawSQL("select szamlaszam from raktarweb_szamlatorzs where szamlaszam between %s and %s",
                #                            (szamlatorzs_kezdeti.szamlaszam, szamlatorzs_vegso.szamlaszam, )))

                '''
                #xml part
                szamlak = Element('szamlak')
                comment = Comment('23_2014 szamlasema alapján')
                szamlak.append(comment)
                export_datuma = SubElement(szamlak, "export_datuma")
                export_datuma.text = str(datetime.date.today())
                ElementTree.ElementTree(szamlak).write("adatexport.xml", encoding="UTF-8",xml_declaration=True)
                '''
                create_xml(szamlakList, szamlatorzs_kezdeti.szamlaszam, szamlatorzs_vegso.szamlaszam)

                return render(request, 'raktarweb/adatexport.html', {
                 'szamlaszam_select_kezdeti_form': szamlaszam_select_kezdeti_form,
                 'szamlaszam_select_vegso_form': szamlaszam_select_vegso_form,
                 'latest_szamlatorzs_list': szamlakList
                })
                # TO DO:: else, error message, must select szamlaszam

    #if a GET (or any other method) we'll create a blank form
    else:
            szamlaszam_select_kezdeti_form = SzamlaszamSelectForm()
            szamlaszam_select_kezdeti_form.fields['kezdeti'] = szamlaszam_select_kezdeti_form.fields['szamlaszam']
            del szamlaszam_select_kezdeti_form.fields['szamlaszam']
            szamlaszam_select_vegso_form = SzamlaszamSelectForm()
            szamlaszam_select_vegso_form.fields['vegso'] = szamlaszam_select_vegso_form.fields['szamlaszam']
            del szamlaszam_select_vegso_form.fields['szamlaszam']

            return render(request, 'raktarweb/adatexport.html', {'szamlaszam_select_kezdeti_form': szamlaszam_select_kezdeti_form,
                                                                 'szamlaszam_select_vegso_form': szamlaszam_select_vegso_form,})
def downloadxml(request):
    logger.info('Starting the xml download')
    xmlFile = open('adatexport.xml', 'r', encoding="utf8")
    response = HttpResponse(xmlFile.read(), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=adatexport.xml'
    response['Content-Length'] = os.path.getsize('adatexport.xml')
    return response
    '''
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    pdf = open('invoice.pdf', 'r')
    response.write(pdf)
    return response
    from django.views.static import serve
    filepath = 'E:/Temp/adatexport.xml'
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
    '''