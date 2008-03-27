from djwiki.wiki.models import *
from django.newforms import *
from django.contrib.auth.models import User,Group
from django.core import validators
from django import oldforms
from django.utils.translation import ugettext as _



class ReadOnlyText(TextInput):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault('attrs',{}).update({'readonly': 'readonly'})
    super(ReadOnlyText, self).__init__(*args, **kwargs)

class WikiEditForm(ModelForm):
  revision = IntegerField(widget=ReadOnlyText())
  title = CharField(widget=ReadOnlyText())
  content = CharField(widget=Textarea(attrs={'rows':40, 'cols':160}))
  markupType = ChoiceField(choices=(('markdown', 'markdown'), ('wikimedia', 'wikimedia')))
  author = CharField(max_length=100,widget=ReadOnlyText())
  class Meta:
    model = WikiPageContent

class ImageUploadForm(Form):
  page = ModelChoiceField(queryset=WikiPageTitle.objects.all())
  contentType = ChoiceField(choices=(('image', 'image'), ('other file', 'other file')))  
  file = ImageField()

class FileUploadForm(Form):
  page = ModelChoiceField(queryset=WikiPageTitle.objects.all())
  file = FileField()


class CreateCategoryForm(Form):
  Name = CharField(max_length=100)


class UserRegistrationForm(Form):
    username =  CharField(required=True)
    firstName = CharField(required=False) 
    secondName = CharField(required=False)
    email = CharField(required=True)
    pass1 = CharField(widget = PasswordInput)
    pass2 = CharField(widget = PasswordInput)

class UserParamForm(Form):
    username =  CharField(required=True,widget=ReadOnlyText())
    firstName = CharField(required=False) 
    secondName = CharField(required=False)
    email = CharField(required=True)
    pass1 = CharField(widget = PasswordInput)
    pass2 = CharField(widget = PasswordInput)

class PermissionsForm(Form):
    from django.contrib.auth.models import User
    User = ModelChoiceField (queryset=User.objects.filter(is_active=True), 
            widget=Select(attrs={'onchange':'javasctipt: document.form.submit();'}))     
 
    Groups = MultipleChoiceField(widget=CheckboxSelectMultiple)
#    Permissions = MultipleChoiceField(widget=CheckboxSelectMultiple)

class CreateGroupForm(Form):
    groupname =  CharField(required=True)

class EditGroupForm(Form):
    groupname =  ModelChoiceField (queryset=Group.objects.all(), 
            widget=Select(attrs={'onchange':'javasctipt: document.form.submit();'}))     
