from djwiki.wiki.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.create_update import *
from django.http import Http404, HttpResponse, HttpResponseRedirect
from djwiki.wiki.myforms import *
from djwiki.settings import MEDIA_ROOT  


def view_page(request, page_title='home'):
  try:
    pageTitle = WikiPageTitle.objects.get(title=page_title)
    page = WikiPageContent.objects.get(title=pageTitle, revision=pageTitle.head_revision)
  except:
    return HttpResponseRedirect("/wiki/%s/create/" % page_title)
  return render_to_response('wiki/view_page.html', {'page': page, 'pageTitle' : pageTitle})

#----------------------------------------------------------------------------------------------------------
def pages_list(request, page_title='home'):
  try:
    page_list = WikiPageTitle.objects.all();
  except:
    return HttpResponseRedirect("/wiki/%s/create/" % page_title)
  return render_to_response('wiki/pages_list.html', 
    {'pages_list' : WikiPageTitle.objects.all(),
     'count' :0,
     'pages_content' : WikiPageContent.objects.all()})

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
  if request.method == 'GET':
    try:
      pageTitle = WikiPageTitle.objects.get(title=page_title)
      page = WikiPageContent.objects.get(title=pageTitle, revision=pageTitle.head_revision)
    except:
      pageTitle = WikiPageTitle()
      pageTitle.title = page_title
      editForm = WikiEditForm(initial={'revision': pageTitle.head_revision, 'title' : pageTitle.title})
    else:
      return HttpResponseRedirect("/wiki/%s/" % page_title)

  elif request.method == 'POST':

    lockErrorMsg = [unicode("Someone has changed this page. Unable to save this version.")]
    try:
      pageTitle, created = WikiPageTitle.objects.get_or_create(title = page_title)  
      if not created:
        editForm.errors['title'] = lockErrorMsg
      else:
        WikiPageContent.objects.get(title = pageTitle, revision = 0)  
        editForm.errors['title'] = lockErrorMsg
    except:
      pass

    editForm = WikiEditForm(request.POST.copy())

    if editForm.is_valid():
      page = editForm.save(commit=False) 
      page.revision = pageTitle.head_revision
      page.title = pageTitle
      pageTitle.save()
      page.save()
      return HttpResponseRedirect("/wiki/%s/" % pageTitle.title)

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
    newPage = editForm.save(commit=False)           

    if newPage.revision != pageTitle.head_revision + 1:
      editForm.errors['title'] = [unicode("Someone has changed this page. Unable to save this version.")]

    if newPage.content == page.content:
      editForm.errors['content'] = [unicode("nothing changed")]

    if editForm.is_valid():
      pageTitle.head_revision = pageTitle.head_revision + 1
      pageTitle.save()
      newPage.title = pageTitle
      newPage.save()
      return HttpResponseRedirect("/wiki/%s/" % newPage.title)
        
  else:
    page.revision = pageTitle.head_revision + 1
    editForm = WikiEditForm(instance = page, initial={'revision': page.revision, 'title' : page_title})

  return render_to_response('wiki/edit_page.html', {'form': editForm, 'page': page})

#------------------------------------------------------------------------

def upload_page(request):
  if request.method == 'GET':
    upForm = UploadForm()
  elif request.method == 'POST':
    upForm = UploadForm(request.POST.copy(),request.FILES)
    if upForm.is_valid():
      filename = upForm.cleaned_data['file'].filename
      server_path = '%s%s' % (MEDIA_ROOT,filename)
      fd = open(server_path, 'wb')  
      fd.write(upForm.cleaned_data['file'].content)  
      fd.close() 
      return HttpResponseRedirect("/wiki/upload/successful/?f=%s" % filename)

  return render_to_response('wiki/upload_page.html', {'form': upForm})

#------------------------------------------------------------------------

def upload_done_page(request):
  if 'f' in request.GET:
    filename = request.GET['f']
    mediawikiLink = '[[Image:%s|%s]]' % (filename, filename)
    markdownLink = '![%s](/static/%s "%s")' % (filename, filename, filename)
    return render_to_response('wiki/upload_successed.html', 
           {'filename': filename, 'mediawikiLink': mediawikiLink, 'markdownLink' : markdownLink})
  else:
    raise Http404
