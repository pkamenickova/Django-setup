from django.conf.urls import patterns, include, url
from project import myadmin 
from django.contrib import admin
admin.autodiscover()
 
urlpatterns = patterns('',
    url(r'^admin/', include(myadmin.site.urls)),
)
