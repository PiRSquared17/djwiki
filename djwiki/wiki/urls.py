from django.conf.urls.defaults import *
from tagging.views import tagged_object_list
from wiki.models import WikiPageContent


urlpatterns = patterns('',

  (r'^tagcloud/$', 'djwiki.wiki.views.tagcloud'),
  (r'^pagesfortag/$', 'djwiki.wiki.views.pagesfortag'),

  (r'^list/$','djwiki.wiki.views.pages_list'),
  (r'^upload/$','djwiki.wiki.views.upload_page'),
  (r'^upload/successful/$','djwiki.wiki.views.upload_done_page'),
  (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/wiki/home/'}),
  (r'^(?P<page_title>[^/]+)/$', 'djwiki.wiki.views.view_page'),
  (r'^(?P<page_title>[^/]+)/edit/$', 'djwiki.wiki.views.edit_page'),
  (r'^(?P<page_title>[^/]+)/create/$', 'djwiki.wiki.views.create_page'),
  (r'^(?P<page_title>[^/]+)/rev/(?P<rev>\d+)/$', 'djwiki.wiki.views.view_revision'),
)
