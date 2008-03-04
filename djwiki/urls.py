from django.conf.urls.defaults import *
from django.contrib.comments.models import FreeComment

urlpatterns = patterns('',
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^wiki/', include('djwiki.wiki.urls')),
     (r'^comments/postfree/', 'views.my_post_free_comment'),
     (r'^comments/', include('django.contrib.comments.urls.comments')),
)
