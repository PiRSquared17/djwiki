from djwiki.wiki.models import *
from django.newforms import ModelForm, TextInput, IntegerField, CharField, ModelChoiceField, Select
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


class WikiEditForm(ModelForm):
  revision = IntegerField(widget=DisabledTextWidget(), required=False)
  title = ModelChoiceField(queryset=WikiPageTitle.objects.all(), widget=DisabledSelectWidget(), required=False)
  class Meta:
    model = WikiPageContent

