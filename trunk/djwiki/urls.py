from django.conf.urls.defaults import *
from djwiki import settings

urlpatterns = patterns('',
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^wiki/', include('djwiki.wiki.urls')),
     (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
