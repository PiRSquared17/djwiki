from django import template

# http://www.freewisdom.org/projects/python-markdown/Installation
import markdown

register = template.Library()

# register the templatetag
@register.filter("markdown_wikify") 
def markdown_wikify(content):
  return markdown.markdown(content)
