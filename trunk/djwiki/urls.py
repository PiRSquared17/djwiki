from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^wiki/', include('djwiki.wiki.urls')),
     (r'^list/', 'djwiki.wiki.views.pages_list'),
)
