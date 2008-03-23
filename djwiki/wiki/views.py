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
from djwiki.wiki.diff import TextDiff
from base64 import b64encode, b64decode
from os import mkdir, remove
import os.path 
from djwiki import settings
from django.contrib.auth.decorators import login_required
from django import template
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Permission

from django.contrib.comments.views.comments import post_free_comment
from django.http import HttpResponseRedirect

lastUserID=[]
lastUserID.append(str(1))

def get_user_name (request):
  if request.user == None or request.user.username=='':
     return 'Anonymous'
 
  if request.user.first_name:
    if request.user.last_name:
      return "%s %s" % (request.user.first_name, request.user.last_name)	
    else: 
      return request.user.first_name
  else:
    return request.user.username
 

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
      'list' : list},
        context_instance=template.RequestContext(request))

#----------------------------------------------------------------------------------------------------------
def tagcloud(request):
  return render_to_response('wiki/tagcloud.html',{},
                        context_instance=template.RequestContext(request)) 

#----------------------------------------------------------------------------------------------------------
def pagesfortag(request):
  if 'f' in request.GET:
    param = request.GET['f']
    return render_to_response('wiki/pagesfortag.html', 
           {'tag': param},
        context_instance=template.RequestContext(request))
  else:
    raise Http404
#----------------------------------------------------------------------------------------------------------
def view_category(request):
  if 'f' in request.GET:
    param = request.GET['f']
  else:
    param = 'Main'

  category, created = WikiCategory.objects.get_or_create(title = param)  
  tag, created = Tag.objects.get_or_create(name=param)
  if request.method == 'GET':
    categoryForm = CreateCategoryForm()  
    return render_to_response('wiki/view_category.html', 
             {'tag' : tag,'form' : categoryForm},
                context_instance=template.RequestContext(request))
  elif request.method == 'POST':
    categoryForm = CreateCategoryForm(request.POST.copy())
    try:
      cat = WikiCategory.objects.get(title = categoryForm.data['Name'])
      alreadyExistsErrorMsg = [unicode("Category with this name is already exists")]
      categoryForm.errors['Name'] = alreadyExistsErrorMsg
      return render_to_response('wiki/view_category.html', 
           {'tag' : tag,'form' : categoryForm},
                context_instance=template.RequestContext(request))
    except:
      cat = WikiCategory.objects.create(title = categoryForm.data['Name'])  
      Tag.objects.add_tag(cat, param)
      return render_to_response('wiki/view_category.html', 
           {'tag' : tag,'form' : categoryForm},
           context_instance=template.RequestContext(request))

#----------------------------------------------------------------------------------------------------------
def register_user(request):
  if request.method == 'GET':
    if request.user is None or request.user.username=="":
      regForm = UserRegistrationForm()  
      register = "1"
    else:
      regForm = UserParamForm(initial={'username': request.user, 
        'pass1':"bad_pass", 'pass2':"bad_pass", 'firstName':request.user.first_name,
        'secondName':request.user.last_name, 'email':request.user.email})  
      register = ""
    return render_to_response('registration/register.html', 
             {'form' : regForm, 'register' : register},
                context_instance=template.RequestContext(request))
  elif request.method == 'POST':
    regForm = UserRegistrationForm(request.POST.copy())
    name = regForm.data['username'];
    useremail = regForm.data['email'];
    pass1 = regForm.data['pass1'];
    pass2 = regForm.data['pass2'];
    firstName = regForm.data['firstName']
    secondName = regForm.data['secondName']
    try:
      user = User.objects.get(username=name);
      if request.user is None:
          regForm.errors['username'] = [unicode("User with this name already exists")]
    except:
      user = None
    if useremail=='' or pass1 == '':
        return render_to_response('registration/register.html', 
           {'form' : regForm},
           context_instance=template.RequestContext(request))
    if pass1==pass2 and user is None:
            user = User.objects.create_user(name,useremail,pass1)
            user.first_name = firstName
            user.last_name = secondName
            user.save()
            user = authenticate(username=name, password=pass1)
            if user.is_active:
                login(request, user)
            return HttpResponseRedirect('/wiki/home')
    elif pass1==pass2:
        user.first_name = firstName
        user.last_name = secondName
        user.email = useremail
        if pass1=="bad_pass":
           pass2=pass1
        else:
           print(pass1)
           user.set_password(pass1)
        user.save()
        return HttpResponseRedirect('/wiki/home')       
    else:
        regForm.errors['pass2'] = [unicode("Passwords doesn't match each other")]
        return render_to_response('registration/register.html', 
           {'form' : regForm},
           context_instance=template.RequestContext(request))

    
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
        diff_content = TextDiff(old_content, page.content).getDiff()
      except:
        diff_content = ''
  except:
    return HttpResponseRedirect("/wiki/%s/create/" % page_title)
  return render_to_response('wiki/view_page.html', {'page': page, 'pageTitle' : pageTitle, 'diff_content':diff_content,
                                                   'user':request.user, 'username':get_user_name(request)},
                        context_instance=template.RequestContext(request))

#----------------------------------------------------------------------------------------------------------
def create_page(request, page_title):
  view_conflict = False
  diff_content = ""

  if request.method == 'GET':
    try:
      pageTitle = WikiPageTitle.objects.get(title=page_title)
      page = WikiPageContent.objects.get(title=pageTitle, revision=pageTitle.head_revision)
    except:
      pageTitle = WikiPageTitle()
      pageTitle.title = page_title
      editForm = WikiEditForm(initial={'revision': pageTitle.head_revision, 'title' : pageTitle.title,
					'author':get_user_name(request)})
    else:
      return HttpResponseRedirect("/wiki/%s/" % page_title)

  elif request.method == 'POST':

    editForm = WikiEditForm(request.POST.copy())
    pageTitle, created = WikiPageTitle.objects.get_or_create(title = page_title)  
    
    if editForm.data['save_anyway'] == 'true' and not created:
      pageTitle.head_revision = pageTitle.head_revision + 1
    elif not created:
      editForm.errors['title'] = [unicode("Someone has changed this page. Unable to save this version.")]
      view_conflict = True
      diff_content = TextDiff(pageTitle.headRevisionContent().content, editForm.cleaned_data['content']).getDiff()

    if editForm.is_valid():
      page = editForm.save(commit=False) 
      page.revision = pageTitle.head_revision
      page.title = pageTitle
      pageTitle.save()
      page.save()
      return HttpResponseRedirect("/wiki/%s/" % pageTitle.title)

  return render_to_response('wiki/edit_page.html', {'form': editForm, 'title':'Create a new page', 
                                                    'view_conflict': view_conflict,
                                                    'diff_content': diff_content },
                                        context_instance=template.RequestContext(request))


#----------------------------------------------------------------------------------------------------------
def edit_page(request, page_title):
  try:
    pageTitle = WikiPageTitle.objects.get(title=page_title)
    page = WikiPageContent.objects.get(title=pageTitle, revision=pageTitle.head_revision)
  except:
    raise Http404

  view_conflict = False
  diff_content = ""

  if request.method == 'POST':
    editForm = WikiEditForm(request.POST.copy())
    newPage = editForm.save(commit=False)           
    
    if editForm.data['save_anyway'] == 'true':
      newPage.revision = pageTitle.head_revision + 1
    else:
      if newPage.revision != pageTitle.head_revision + 1:
        editForm.errors['title'] = [unicode("Someone has changed this page. Unable to save this version.")]
        view_conflict = True
        diff_content = TextDiff(pageTitle.headRevisionContent().content, newPage.content).getDiff()

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
    editForm = WikiEditForm(instance = page, initial={'revision': page.revision, 'title' : page_title,
						      'author':get_user_name(request)})

  return render_to_response('wiki/edit_page.html', {'form': editForm, 'page': page, 
                                                    'title': 'Edit page', 'view_conflict': view_conflict,
                                                    'diff_content': diff_content },
                                        context_instance=template.RequestContext(request))

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

  return render_to_response('wiki/upload_page.html', {'form': upForm},
                        context_instance=template.RequestContext(request))

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
             {'filename': file.path(), 'mediawikiLink': mediawikiLink, 'markdownLink' : markdownLink, 'type':file.type},
                                        context_instance=template.RequestContext(request))
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

#------------------------------------------------------------------------
def view_revisions(request, page_title):
#  try:
  pageTitle = WikiPageTitle.objects.get(title=page_title)
  revisions = WikiPageContent.objects.filter(title=pageTitle)
  choices = []
  for rev in revisions:
    text = rev.title.title + ' rev ' + str(rev.revision) 
    choices.append((str(rev.revision), text))
  print(choices)


  if request.method == 'GET':
    form = Form()
    form.base_fields['Revisions'] = MultipleChoiceField(choices=choices, widget=CheckboxSelectMultiple())


  elif request.method == 'POST':
    form = Form(request.POST)
    if form.is_valid():
      selected = form.cleaned_data['Revisions'] 
      if len(selected) != 2:
        form.errors['Revisions'] = [unicode('You must select exactly two revisions for diff')]
      else:
        rev1 = selected[0]
        rev2 = selected[1]
        response = HttpResponseRedirect("/wiki/%s/diff/?r1=%s&r2=%s" % (page_title, rev1, rev2))
        return response

  return render_to_response('wiki/rev_list.html', {'list': revisions, 'form': form},
                        context_instance=template.RequestContext(request))
#  except:
#    raise Http404

#------------------------------------------------------------------------

def diff_page(request, page_title):
  try:
    if 'r1' in request.GET and 'r2' in request.GET:
      pageTitle = WikiPageTitle.objects.get(title=page_title)
      rev1 = WikiPageContent.objects.get(title = pageTitle, revision = request.GET['r1'])
      rev2 = WikiPageContent.objects.get(title = pageTitle, revision = request.GET['r2'])
      diff_content = TextDiff(rev1.content, rev2.content).getDiff()
      return render_to_response('wiki/diff_page.html', {'rev1': rev1, 'rev2': rev2, 'diff_content' : diff_content},
                                        context_instance=template.RequestContext(request))
    else:
      raise Http404
  except:
    raise Http404

#------------------------------------------------------------------------
def view_permissions(request):
  from django.db import models
  from django.db.models import get_models
  from django.contrib.auth.models import Group

  perms = request.user.user_permissions
  choices = []
  permissions = []
  init=[]
  i = 0
  if 'f' in request.GET:
     userid = request.GET['f']
     EditUser = User.objects.get(id=userid) 
  else:
     userid = request.user.id
     EditUser = request.user
  lastUserID = EditUser.id

  print("Edit permissions for user")
  print("Name %s ID %s" % (EditUser.username,userid))

  groupChoices = []
  groupInit = []
  groups = []
  i=0
  for group in Group.objects.all():
    if group in EditUser.groups.all():
      groupChoices.append((str(i),str(group.name),"1"))
      groupInit.append(str(i))
    else:
      groupChoices.append((str(i),str(group.name)))
    groups.append(group)
    i=i+1

#  for perm in EditUser.user_permissions.all():
#    print(perm)
  i=0
  for perm in Permission.objects.all():
    text = '%s' % perm
    choices.append((str(i), text))
    if EditUser.has_perm("%s.%s" %(perm.content_type.app_label,perm.codename)):
      init.append(str(i))
    permissions.append(perm);
    i=i+1

  if request.method == 'GET':
    lastUserID = EditUser.id
    form = PermissionsForm(initial = {'Permissions': init, 'User': str(userid),
				      'Groups':groupInit});
    form.base_fields['Permissions'] = MultipleChoiceField(choices=choices, widget=CheckboxSelectMultiple(),
                                      initial = {'choices': 0})
    #form.base_fields['Groups'] = MultipleChoiceField(choices=groupChoices, widget=CheckboxSelectMultiple())

  elif request.method == 'POST':
    form = PermissionsForm(request.POST)
    try:
      print(form.data.getlist('Groups'))
      for s in form.data['Groups']:
        print(s)
    except:
      i=0
    uname = form.data.getlist('User')[0];
    EditUser = User.objects.get(id=uname)
    print("***************")
    if str(uname) == str(lastUserID):
      print('NEED PARAM UPDATE')
      permsSelection = form.data.getlist('Permissions') 
      EditUser.user_permissions.clear()
      for sel in permsSelection:
        print(sel)
        EditUser.user_permissions.add(permissions[int(sel)])
      EditUser.save()
      groupsSelection = form.data.getlist('Groups') 
      EditUser.groups.clear()
      for sel in groupsSelection:
        print(sel)
        EditUser.groups.add(groups[int(sel)])
      EditUser.save()
    else:
      print("OLD USER, NO UPDATE") 
    print("***************")    
    lastUserID = EditUser.id
    url = '/wiki/permissions/?f=%s' % EditUser.id
    return HttpResponseRedirect(url)


  print("HHHHHH")
  print(groupChoices[0][0]) 
 
  return render_to_response('wiki/perm_list.html', {'list': perms, 'form': form,
                          'groupChoices': groupChoices},
                        context_instance=template.RequestContext(request))
