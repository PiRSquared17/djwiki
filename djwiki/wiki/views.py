from djwiki.wiki.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.create_update import *
from django.http import Http404, HttpResponse, HttpResponseRedirect
from djwiki.wiki.myforms import *
from djwiki.settings import MEDIA_ROOT 
from tagging.models import Tag
from tagging.views import tagged_object_list
from tagging.utils import get_tag
from tagging.utils import calculate_cloud
from djwiki.wiki.diff import textDiff
from base64 import b64encode, b64decode
from os import mkdir, remove
import os.path 
from djwiki import settings



from django.contrib.comments.views.comments import post_free_comment
from django.http import HttpResponseRedirect

def my_post_free_comment(request):
	if request.has_key('url') and not request.has_key('preview'):
		response = post_free_comment(request)
		
		# Check there's a url to redirect to, and that post_free_comment worked
		if len(request['url'].strip()) > 0 and isinstance(response, HttpResponseRedirect):
			return HttpResponseRedirect(request['url'])
		
		# Fall back on the default post_free_comment response
		return response
	
	return post_free_comment(request)

#----------------------------------------------------------------------------------------------------------

def tags_list(request, page_title='home'):
  list = tagged_object_list(request,WikiPageContent,'hi')
  #cloud = calculate_cloud('hi')
  try:
    page_list = WikiPageTitle.objects.all();
  except:
    return HttpResponseRedirect("/wiki/%s/create/" % page_title)
  return render_to_response('wiki/tags_list.html', 
    {'pages_list' : WikiPageTitle.objects.all(),
     'count' :0,
     'pages_content' : WikiPageContent.objects.all(),
      'list' : list})

#----------------------------------------------------------------------------------------------------------
def tagcloud(request):
  return render_to_response('wiki/tagcloud.html',{}) 

#----------------------------------------------------------------------------------------------------------
def pagesfortag(request):
  if 'f' in request.GET:
    param = request.GET['f']
    return render_to_response('wiki/pagesfortag.html', 
           {'tag': param})
  else:
    raise Http404
#----------------------------------------------------------------------------------------------------------
def view_category(request):
  if 'f' in request.GET:
    param = request.GET['f']
  else:
    param = 'Main'
  category = WikiCategory.objects.get_or_create(title = param)  
  category = WikiCategory.objects.get(title = param)
  tag = Tag.objects.get_or_create(name=param)
  tag = Tag.objects.get(name= param)
  if request.method == 'GET':
    editForm = CreateCategoryForm()  
    return render_to_response('wiki/view_category.html', 
             {'category': category,'tag' : tag,'form' : editForm})
  elif request.method == 'POST':
    editForm = CreateCategoryForm(request.POST.copy())
    try:
      cat = WikiCategory.objects.get(title = editForm.data['Name'])
      editForm = CreateCategoryForm()  
      alreadyExistsErrorMsg = [unicode("Category with this name is already exists")]
      editForm.errors['Name'] = alreadyExistsErrorMsg
      return render_to_response('wiki/view_category.html', 
           {'category': category,'tag' : tag,'form' : editForm})
    except:
      cat = WikiCategory.objects.create(title = editForm.data['Name'])  
#      cat = WikiCategory.objects.get(title = editForm.data['Name'])
      Tag.objects.add_tag(cat, param)
      print('error');
      return render_to_response('wiki/view_category.html', 
           {'category': category,'tag' : tag,'form' : editForm})

#----------------------------------------------------------------------------------------------------------

def view_page(request, page_title, rev, is_head):
  try:
    pageTitle = WikiPageTitle.objects.get(title=page_title)
    if str(pageTitle.head_revision) == rev and not is_head:
      return HttpResponseRedirect("/wiki/%s/" % page_title)
    else:
      if is_head:
        page = pageTitle.headRevisionContent() 
      else:
        page = WikiPageContent.objects.get(title=pageTitle, revision=rev)
      try:
        old_content = WikiPageContent.objects.get(title=pageTitle, revision=page.revision-1).content
        diff_content = textDiff(old_content, page.content)
      except:
        diff_content = ''
  except:
    return HttpResponseRedirect("/wiki/%s/create/" % page_title)
  return render_to_response('wiki/view_page.html', {'page': page, 'pageTitle' : pageTitle, 'diff_content':diff_content})

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
    upForm = ImageUploadForm()
  elif request.method == 'POST':
    if request.POST['contentType'] == 'image':
      type = 'image'
      upForm = ImageUploadForm(request.POST.copy(),request.FILES)
    else:
      type = 'file'
      upForm = FileUploadForm(request.POST.copy(),request.FILES)
 
    if upForm.is_valid():
      pageTitle = upForm.cleaned_data['page']
      filename = upForm.cleaned_data['file'].filename
      file, created = UploadedFile.objects.get_or_create(name=filename, page=pageTitle, type=type)
      file.data = b64encode(upForm.cleaned_data['file'].content) 
      file.save()

      abs_path = settings.MEDIA_ROOT + type + '/' + pageTitle.title + '/' + filename
      if(os.path.exists(abs_path)):
        os.remove(abs_path)

      return HttpResponseRedirect("/wiki/upload/successful/?p=%s&f=%s&t=%s" % (file.page.title, file.name, file.type))

  return render_to_response('wiki/upload_page.html', {'form': upForm})

#------------------------------------------------------------------------

def upload_done_page(request):
  try:
    if 'p' in request.GET and 'f' in request.GET and 't' in request.GET:
      pageTitle = WikiPageTitle.objects.get(title=request.GET['p'])
      file = UploadedFile.objects.get(page=pageTitle, name=request.GET['f'], type=request.GET['t'])

      if file.type == 'image':
        mediawikiLink = '[[Image:%s|%s]]' % (file.path(), file.name)
        markdownLink = "![%s](/wiki/static/image/%s %s)" % (file.path(), file.path(), file.name)
      else:
        mediawikiLink = '[[File:%s|%s]]' % (file.path(), file.name)
        markdownLink = "[%s](/wiki/static/file/%s)" % (file.path(), file.path())
 
      return render_to_response('wiki/upload_successed.html', 
             {'filename': file.path(), 'mediawikiLink': mediawikiLink, 'markdownLink' : markdownLink, 'type':file.type})
    else:
      raise Http404
  except:
    raise Http404

#------------------------------------------------------------------------

def view_file(request, file, page, type):
  if type == 'image':
    abs_path = settings.MEDIA_ROOT + 'image/' + page + '/'
  elif type == 'file':
    abs_path = settings.MEDIA_ROOT + 'file/' + page + '/'
  else:  
    pass
#    raise Http404
 
  if(not os.path.exists(abs_path)):
    mkdir(abs_path)

  abs_path += file

  if(not os.path.exists(abs_path)):
    try:
      pageTitle = WikiPageTitle.objects.get(title = page)
      fileObj = UploadedFile.objects.get(name = file, page = pageTitle, type = type)
      f = open(abs_path, 'wb')
      f.write(b64decode(fileObj.data))
      f.close()
    except:
      raise Http404

  return HttpResponseRedirect("/wiki/dynamic/" + type + '/' + page + '/' + file)  
