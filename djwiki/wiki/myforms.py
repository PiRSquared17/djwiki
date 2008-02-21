from djwiki.wiki.models import *
from django.newforms import *
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe
from django.newforms.util import flatatt

class DisabledTextWidget(TextInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs',{}).update({'disabled': 'True'})
        super(DisabledTextWidget, self).__init__(*args, **kwargs)

class DisabledSelectWidget(Select):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs',{}).update({'disabled': 'True'})
        super(DisabledSelectWidget, self).__init__(*args, **kwargs)

class BigTextWidget(Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs',{}).update({'cols': '160', 'rows': '40'})
        super(BigTextWidget, self).__init__(*args, **kwargs)


class WikiEditForm(ModelForm):
  revision = IntegerField(widget=DisabledTextWidget(), required=False)
  title = ModelChoiceField(queryset=WikiPageTitle.objects.all(), widget=DisabledSelectWidget(), required=False)
  content = CharField(widget=BigTextWidget())
  markup_types = (('markdown', 'markdown'), ('wikimedia', 'wikimedia'))
  markupType = ChoiceField(choices=markup_types)

  class Meta:
    model = WikiPageContent

