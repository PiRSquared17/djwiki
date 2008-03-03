from django.conf.urls.defaults import *
from djwiki import settings
from django.contrib.comments.models import FreeComment


urlpatterns = patterns('',
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^wiki/', include('djwiki.wiki.urls')),
     (r'^comments/', include('django.contrib.comments.urls.comments')),
     (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
