from djwiki.wiki.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.create_update import *
from django.http import Http404, HttpResponse, HttpResponseRedirect
from djwiki.wiki.myforms import *

def view_page(request, page_title='home'):
  try:
    pageTitle = WikiPageTitle.objects.get(title=page_title)
    page = WikiPageContent.objects.get(title=pageTitle, revision=pageTitle.head_revision)
    return render_to_response('wiki/view_page.html', {'page': page, 'pageTitle' : pageTitle})
  except:
    return create_page(request, page_title)

#----------------------------------------------------------------------------------------------------------

def view_revision(request, page_title, rev):
  try:
    pageTitle = WikiPageTitle.objects.get(title=page_title)
    if str(pageTitle.head_revision) == rev:
      return HttpResponseRedirect("/wiki/%s/" % page_title)
    else:
      page = WikiPageContent.objects.get(title=pageTitle, revision=rev)
      return render_to_response('wiki/view_page.html', {'page': page, 'pageTitle' : pageTitle})
  except:
    return view_page(request, page_title)

#----------------------------------------------------------------------------------------------------------

def create_page(request, page_title):
  try:
    pageTitle = WikiPageTitle.objects.get(title=page_title)
  except:
    pageTitle = WikiPageTitle()
    pageTitle.title = page_title
    pageTitle.save()
  try:
    page = WikiPageContent()
    page.title = pageTitle
    page.revision = pageTitle.head_revision     
  except:
    return view_page(request, page_title)

  if request.method == 'POST':
    editForm = WikiEditForm(request.POST.copy())

    if editForm.is_valid():
      page = editForm.save(commit=False) 
      page.revision = pageTitle.head_revision
      page.title = pageTitle
      pageTitle.save()
      page.save()
      return HttpResponseRedirect("/wiki/%s/" % pageTitle.title)
  else:
    editForm = WikiEditForm(instance=page)

  return render_to_response('wiki/create_page.html', {'form': editForm})


#----------------------------------------------------------------------------------------------------------

def edit_page(request, page_title):
  try:
    pageTitle = WikiPageTitle.objects.get(title=page_title)
    page = WikiPageContent.objects.get(title=pageTitle, revision=pageTitle.head_revision)
  except:
    raise Http404

  if request.method == 'POST':
    editForm = WikiEditForm(request.POST.copy())


    if editForm.is_valid():
      page = editForm.save(commit=False) 
      pageTitle.head_revision = pageTitle.head_revision + 1
      page.revision = pageTitle.head_revision
      pageTitle.save()
      page.title = pageTitle
      page.save()
      return HttpResponseRedirect("/wiki/%s/" % page.title)
  else:
    page.revision = pageTitle.head_revision + 1
    editForm = WikiEditForm(instance = page)

  return render_to_response('wiki/edit_page.html', {'form': editForm, 'page': page})
