from django.db import models
import datetime

class WikiPageTitle(models.Model):
  title = models.CharField(max_length=100, unique=True)
  head_revision = models.IntegerField(default=0)

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
