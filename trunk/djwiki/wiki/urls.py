from django.conf.urls.defaults import *
from tagging.views import tagged_object_list
from wiki.models import WikiPageTitle, WikiPageContent
from django.contrib.comments.models import FreeComment
from djwiki import settings


urlpatterns = patterns('django.views.generic.simple',
  (r'^list/$','direct_to_template', {'template':'wiki/pages_list.html',
                                     'extra_context': {'title':'Page list', 
                                                       'list':WikiPageTitle.objects.all()}}),
  (r'^$', 'redirect_to', {'url': '/wiki/home/'}),
)

urlpatterns += patterns('',
  (r'^tagcloud/$', 'djwiki.wiki.views.tagcloud'),
  (r'^register/$', 'djwiki.wiki.views.register_user'),
  (r'^permissions/$', 'djwiki.wiki.views.view_permissions'),
  (r'^pagesfortag/$', 'djwiki.wiki.views.pagesfortag'),
  (r'^categories/$', 'djwiki.wiki.views.view_category'),
  (r'^upload/$','djwiki.wiki.views.upload_page'),
  (r'^upload/successful/$','djwiki.wiki.views.upload_done_page'),
  (r'^(?P<page_title>[^/]+)/$', 'djwiki.wiki.views.view_page', {'rev':0,'is_head':True}),
  (r'^(?P<page_title>[^/]+)/edit/$', 'djwiki.wiki.views.edit_page'),  
  (r'^(?P<page_title>[^/]+)/create/$', 'djwiki.wiki.views.create_page'),
  (r'^(?P<page_title>[^/]+)/rev/$', 'djwiki.wiki.views.view_revisions'),
  (r'^(?P<page_title>[^/]+)/rev/(?P<rev>\d+)/$', 'djwiki.wiki.views.view_page', {'is_head':False}),
  (r'^(?P<page_title>[^/]+)/diff/$', 'djwiki.wiki.views.diff_page'),
  (r'^static/(?P<type>[^/]*)/(?P<page>[^/]*)/(?P<file>[^/]*)/$', 'djwiki.wiki.views.view_file'),
  (r'^dynamic/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)



