from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'raktarsite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^raktarweb/', include('raktarweb.urls')),
    url(r'^raktarweb/', include('raktarweb.urls', namespace="raktarweb")),
    url(r'^admin/', include(admin.site.urls)),
    url('^', include('django.contrib.auth.urls'))
)
