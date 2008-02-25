from djwiki.wiki.models import *
from django.newforms import *

class ReadOnlyText(TextInput):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault('attrs',{}).update({'readonly': 'readonly'})
    super(ReadOnlyText, self).__init__(*args, **kwargs)

class WikiEditForm(ModelForm):
  revision = IntegerField(widget=ReadOnlyText())
  title = CharField(widget=ReadOnlyText())
  content = CharField(widget=Textarea(attrs={'rows':40, 'cols':160}))
  markupType = ChoiceField(choices=(('markdown', 'markdown'), ('wikimedia', 'wikimedia')))

  class Meta:
    model = WikiPageContent

class UploadForm(Form):
  file = ImageField()
