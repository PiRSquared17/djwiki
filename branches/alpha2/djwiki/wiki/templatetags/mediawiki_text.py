from django import template
import mediawiki

register = template.Library()

@register.filter("mediawiki_wikify") 
def mediawiki_wikify(content):
  return mediawiki.parse(content)
