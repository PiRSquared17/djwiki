from django.conf.urls.defaults import *
from django.contrib.comments.models import FreeComment

urlpatterns = patterns('',
     (r'^accounts/login/$', 'django.contrib.auth.views.login'),  
     (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^wiki/', include('djwiki.wiki.urls')),
     (r'^comments/postfree/', 'views.my_post_free_comment'),
     (r'^comments/', include('django.contrib.comments.urls.comments')),
     (r'^xmlrpc/$', 'djwiki.wiki.xmlrpc.rpc_handler'),
)
