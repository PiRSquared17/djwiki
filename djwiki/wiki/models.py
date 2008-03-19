from django.db import models
from tagging.models import Tag
from tagging.fields import TagField
import datetime
import tagging

class WikiPageTitle(models.Model):
  title = models.CharField(max_length=100, unique=True)
  head_revision = models.IntegerField(default=0)

  def headRevisionContent(self):
        return WikiPageContent.objects.get(title=self,revision=self.head_revision)

  class Admin:
    pass
  def __unicode__(self):
    return self.title
  

class WikiPageContent(models.Model):
  title = models.ForeignKey(WikiPageTitle)
  content = models.TextField()
  author = models.CharField(max_length=100)
  revision = models.IntegerField(default=0)
  modificationTime = models.DateTimeField(auto_now_add=True) 
  markupType = models.CharField(max_length=100)
  tags = TagField()
  class Meta:
    unique_together = ("title", "revision")

  class Admin:
    pass

  def __unicode__(self):
    return self.title.title + " rev " + str(self.revision)      

  def prev_revision(self):
   if(self.revision > 0):
     return self.revision - 1
   else:
     return self.revision

  def next_revision(self):
   if(self.revision < self.title.head_revision):
     return self.revision + 1
   else:
     return self.revision
  def get_absolute_url(self):
    return ("/wiki/%s/rev/%d/" % (self.title,self.revision))
  class Meta:
        permissions = (
            ("can_view", "Can view"),
            ("can_edit", "Can edit"),
        )

class WikiCategory(models.Model):
  title = models.CharField(max_length=100, unique=True)
  tags = TagField()

  class Admin:
    pass

  def __unicode__(self):
    return self.title      

class UploadedFile(models.Model):
  name = models.CharField(max_length=100)
  page = models.ForeignKey(WikiPageTitle)
  data = models.TextField()
  type = models.CharField(max_length=100)

  class Admin:
    pass

  def path(self):
    return self.page.title + '/' + self.name

  def __unicode__(self):
    return self.path()      

  class Meta:
    unique_together = ("name", "page", "type")
    permissions = (
            ("can_upload", "Can upload"),
        )

