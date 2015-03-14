# Timeline #

Links:
  * code.google.com
  * w3c.org: xhtml primer, css primer
  * read about locking [google groups thread](http://groups.google.com/group/django-users/browse_thread/thread/e9db1349014aa1f4/9a697f65a617b5f6?#9a697f65a617b5f6)
  * ER-diagram sample [image](http://www.conceptdraw.com/products/img/ScreenShots/cd5/software/SampleDatabaseLayout.gif)
  * html-diff [python script](http://web.archive.org/web/20040416194325/http://www.webwareforpython.org/~ianb/w4py.org/Wiki/lib/htmldiff.py)
  * [django-tagging](http://code.google.com/p/django-tagging/)
  * [django.contrib.freecomments](http://code.djangoproject.com/wiki/UsingFreeComment)
  * [trouble with blob fields](http://blog.buffis.com/?p=49)
  * [something about ssl](http://www.djangosnippets.org/snippets/240/)
  * [Django authorization](http://www.djangoproject.com/documentation/authentication/)

Alpha1 - completed on 2008-02-28: _**branch https://djwiki.googlecode.com/svn/branches/alpha1**_
  * pagelist _**SAN - base functions rev #27**_
  * nice wiki/list page design _**Done**_
  * mysql _**ALeRT - done, check [this](http://code.google.com/p/djwiki/wiki/deployment) out**_
  * wikimarkup + markdown (or-or) _**ALeRT - done rev #10**_
  * attachments _**SAN rev #40 base functions**_
  * error checking _**Done**_
  * simple concurrent blocking _**ALeRT - done rev #23**_
  * navigation menu base functions _**SAN rev #27**_
  * remove css code from templates _**Done**_

Spec ():
  * Design (ER-diagram) _**Done [see here ](http://code.google.com/p/djwiki/wiki/Alpha1ERDiagram)**_

Alpha2 (2008-03-13):
  * xmlrpc (SQL, transactions) _**Done**_
  * tags
    * Tag line in page view  _**rev #100**_
    * List of pages marked with tag   _**rev #100**_
    * Simle Tag Cloud page _**rev #100**_
  * categories (hierarchy) _**rev #107**_
  * comments _**Done**_
  * diff _**Done**_
  * diff after conflicts _**Done**_
  * revision list (diff of any 2 revisions) _**Done**_
  * file model, bind file to wikiPage _**Done**_
  * store files in db (in a base64 text field) _**Done**_

Spec ():
  * Design (ER-diagram) _**Done**_

Beta (): completed 27.03.08
  * xmlrpc (SQL, transactions) _**Done**_
    * provide functions to manipulte with wiki-pages, categories and etc. _**Done**_
    * connect to the DB directly via mod MySqlDb _**Done**_
  * authorization _**Done**_
  * roles
    * base privileges _**Done**_
    * hierarchy _**Done**_
  * ssl