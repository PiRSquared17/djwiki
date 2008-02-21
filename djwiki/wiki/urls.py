from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/wiki/home/'}),
  (r'^(?P<page_title>\w+)/$', 'djwiki.wiki.views.view_page'),
  (r'^(?P<page_title>[^/]+)/edit/$', 'djwiki.wiki.views.edit_page'),
  (r'^(?P<page_title>[^/]+)/rev/(?P<rev>\d+)/$', 'djwiki.wiki.views.view_revision'),
)
