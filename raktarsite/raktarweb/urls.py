__author__ = 'takacs'

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('thanks', views.thanks, name='thanks'),
    url(r'^register/$', views.register, name='register'),  # ADD NEW PATTERN!
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^raktar/$', views.raktar, name='raktar'),
    url(r'^ujszamla/$', views.ujszamla, name='ujszamla'),
    url(r'^sztornozas/$', views.sztornozas, name='sztornozas'),
    url(r'^ujsztornozas/$', views.ujsztornozas, name='ujsztornozas'),
    url(r'^adatexport/$', views.adatexport, name='adatexport'),
    url(r'^downloadxml/$', views.downloadxml, name='downloadxml'),
    #url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    #url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    #url(r'^(?P<szamlatorzs_id>[0-9]+)/$', views.detail, name='detail'),
    #url(r'^(?P<szamlatorzs_id>[0-9]+)/vote/$', views.vote, name='vote'),
    # ez mukodik
    #url(r'^(?P<szamlatorzs_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<szamlatorzs_id>[0-9]+)/(?P<peldany>[0-9]{1})/$', views.detail, name='detail'),
    url(r'^(?P<szamlatorzs_id>[0-9]+)/results/$', views.results, name='results'),
    #url('pdf', views.pdf, name='pdf'),
    url('sikeres', views.sikeres, name='sikeres'),
    url('printinvoice', views.printinvoice, name='printinvoice'),
    url('jsonexample', views.jsonexample, name='jsonexample'),

]
