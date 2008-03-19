# Patchless XMLRPC Service for Django
# Kind of hacky, and stolen from Crast on irc.freenode.net:#django
# Self documents as well, so if you call it from outside of an XML-RPC Client
# it tells you about itself and its methods
#
# Brendan W. McAdams <brendan.mcadams@thewintergrp.com>

# SimpleXMLRPCDispatcher lets us register xml-rpc calls w/o
# running a full XMLRPC Server.  It's up to us to dispatch data

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
import MySQLdb
import datetime
from djwiki import settings
from django.contrib.auth import authenticate


# Create a Dispatcher; this handles the calls and translates info to function maps
dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None) # Python 2.5

#----------------------------------------------------------------------------------------------------------

try:
  myConnection = MySQLdb.connect(host = settings.DATABASE_HOST,
                                 port = int(settings.DATABASE_PORT),
                                 user = settings.DATABASE_USER,
                                 passwd = settings.DATABASE_PASSWORD,
                                 db = settings.DATABASE_NAME)
except MySQLdb.Error, e:
  myConnection = None

#----------------------------------------------------------------------------------------------------------

#@user_passes_test(lambda u: u.has_perm('WikiPageContent.can_use_xmlrpc'))
def rpc_handler(request):
        """
        the actual handler:
        if you setup your urls.py properly, all calls to the xml-rpc service
        should be routed through here.
        If post data is defined, it assumes it's XML-RPC and tries to process as such
        Empty post assumes you're viewing from a browser and tells you about the service.
        """

        response = HttpResponse()
        if len(request.POST):
                user = None 
                try:
                  username = request.GET['u']
                  password = request.GET['p']
                  user = authenticate(username=username, password=password)
                except:
                  pass

                if (user == None) or not user.is_active or not user.has_perm('WikiPageContent.can_use_xmlrpc'):
                  error_msg = """<?xml version='1.0'?>
                                 <methodResponse>
                                 <params>
                                 <param>
                                 <value><string>You don't have permissions to use xml-rpc.</string></value>
                                 </param>
                                 </params>
                                 </methodResponse>"""

                  response.write(error_msg)
                else:
                  response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
                 
        else:
                response.write("<b>This is an XML-RPC Service.</b><br>")
                response.write("You need to invoke it using an XML-RPC Client!<br>")
                response.write("The following methods are available:<ul>")
                methods = dispatcher.system_listMethods()

                for method in methods:
                        # right now, my version of SimpleXMLRPCDispatcher always
                        # returns "signatures not supported"... :(
                        # but, in an ideal world it will tell users what args are expected
                        sig = dispatcher.system_methodSignature(method)

                        # this just reads your docblock, so fill it in!
                        help =  dispatcher.system_methodHelp(method)

                        response.write("<li><b>%s</b>: [%s] %s" % (method, sig, help))

                response.write("</ul>")
                response.write('<a href="http://www.djangoproject.com/"> <img src="http://media.djangoproject.com/img/badges/djangomade124x25_grey.gif" border="0" alt="Made with Django." title="Made with Django."></a>')

        response['Content-length'] = str(len(response.content))
        return response

#----------------------------------------------------------------------------------------------------------

def insert_tags(modelName, obj_id, tags_str):
  cursor = myConnection.cursor()

  cursor.execute("SELECT id FROM django_content_type WHERE (model = '%s')" % modelName)    
  row = cursor.fetchone()
  if row == None:
    cursor.close()
    return False
  content_type = row[0]

  tag_ids = []
  for tag in tags_str.split(" "):
    cursor.execute("SELECT id FROM tagging_tag WHERE name = '%s'" % tag)    
    row = cursor.fetchone()
    if row == None:
      cursor.execute("INSERT INTO tagging_tag (name) VALUES('%s')" % tag)    
      tag_ids.append(str(myConnection.insert_id()))
    else:
      tag_ids.append(str(row[0]))

  for tag_id in tag_ids:
    cursor.execute("""INSERT INTO tagging_taggeditem (tag_id, content_type_id, object_id) 
                      VALUES (%s, %s, %s)""" % (tag_id, content_type, obj_id))    

  cursor.close()
  return True

#----------------------------------------------------------------------------------------------------------

def update_page(title, content, author, markupType, tags_str):
  if settings.DATABASE_ENGINE != 'mysql':
    return "error: xml-rpc not supported"
  if myConnection == None:
    return "error: no connection with db server"

  cursor = myConnection.cursor()
  cursor.execute("SELECT id, title, head_revision FROM wiki_wikipagetitle WHERE title = '%s'" % title)
  row = cursor.fetchone()
  if row == None:
    return "error: no such page"
  title_id = row[0]
  head_rev = row[2]

  new_rev = str(head_rev + 1)

  cursor.execute("UPDATE wiki_wikipagetitle SET head_revision = %s WHERE id = %s" % (new_rev, title_id))
  cursor.execute("""INSERT INTO wiki_wikipagecontent (title_id, content, author, revision, modificationTime, markupType, tags)
                    VALUES(%s, '%s', '%s', %s, '%s', '%s', '%s')  
                 """ %(title_id, content, author, new_rev, MySQLdb.times.format_TIMESTAMP(datetime.datetime.now()), markupType, tags_str))

  insert_tags("wikipagecontent", myConnection.insert_id(), tags_str)

  cursor.close()
  myConnection.commit()
  return ""

#----------------------------------------------------------------------------------------------------------

def create_page(title, content, author, markupType, tags_str):
  if settings.DATABASE_ENGINE != 'mysql':
    return "error: xml-rpc not supported"

  if myConnection == None:
    return "error: no connection with db server"
  cursor = myConnection.cursor()
  cursor.execute("SELECT id, title, head_revision FROM wiki_wikipagetitle WHERE title = '%s'" % title)
  row = cursor.fetchone()
  if row != None:
    return "error: page already exists"
  cursor.execute("""INSERT INTO wiki_wikipagetitle (title, head_revision) 
                    VALUES ('%s', 0)""" % title)    

  title_id = myConnection.insert_id()

  cursor.execute("""INSERT INTO wiki_wikipagecontent (title_id, content, author, revision, modificationTime, markupType, tags)
                    VALUES(%s, '%s', '%s', 0, '%s', '%s', '')  
                 """ %(title_id, content, author, MySQLdb.times.format_TIMESTAMP(datetime.datetime.now()), markupType))

  insert_tags("wikipagecontent", myConnection.insert_id(), tags_str)

  cursor.close()
  myConnection.commit()
  return ""

#----------------------------------------------------------------------------------------------------------

def get_page_list():
  if settings.DATABASE_ENGINE != 'mysql':
    return "error: xml-rpc not supported"

  if myConnection == None:
    return "error: no connection with db server"
  cursor = myConnection.cursor()
  cursor.execute("SELECT * FROM wiki_wikipagetitle")
  rows = cursor.fetchall()
  cursor.close()
  return rows

#----------------------------------------------------------------------------------------------------------

def get_page(title):
  if settings.DATABASE_ENGINE != 'mysql':
    return "error: xml-rpc not supported"
  if myConnection == None:
    return "error: no connection with db server"
  cursor = myConnection.cursor()
  cursor.execute("SELECT id, head_revision FROM wiki_wikipagetitle WHERE title = '%s'" % title)
  row = cursor.fetchone()
  if row == None:
    return "error: no such page"
  title_id = row[0]
  head_rev = row[1]
  cursor.execute("SELECT * FROM wiki_wikipagecontent WHERE (title_id = %s) and (revision = %s)" % (title_id, head_rev))
  row = cursor.fetchone()
  cursor.close()
  return row

#----------------------------------------------------------------------------------------------------------

def get_revision(title, rev):
  if settings.DATABASE_ENGINE != 'mysql':
    return "error: xml-rpc not supported"
  if myConnection == None:
    return "error: no connection with db server"
  cursor = myConnection.cursor()
  cursor.execute("SELECT id FROM wiki_wikipagetitle WHERE title = '%s'" % title)
  row = cursor.fetchone()
  if row == None:
    return "error: no such page"
  title_id = row[0]
  cursor.execute("SELECT * FROM wiki_wikipagecontent WHERE (title_id = %s) and (revision = %s)" % (title_id, rev))
  row = cursor.fetchone()
  if row == None:
    return "error: no such revision"
  cursor.close()
  return row

#----------------------------------------------------------------------------------------------------------

def get_category(name):
  if settings.DATABASE_ENGINE != 'mysql':
    return "error: xml-rpc not supported"
  if myConnection == None:
    return "error: no connection with db server"

  cursor = myConnection.cursor()

  cursor.execute("SELECT id FROM wiki_wikicategory WHERE (title = '%s')" % name)    
  row = cursor.fetchone()
  if row == None:
    return "error: no such category"
  
  cursor.execute("SELECT id FROM tagging_tag WHERE (name = '%s')" % name)    
  row = cursor.fetchone()
  if row == None:
    return "error: no such category"
  cat_tag_id = row[0]

  cursor.execute("SELECT id FROM django_content_type WHERE (model = 'wikicategory')")    
  row = cursor.fetchone()
  if row == None:
    cursor.close()
    return "error"

  content_type = row[0]

  cursor.execute("""SELECT title 
                    FROM wiki_wikicategory
                    WHERE id in ( SELECT object_id 
                                  FROM tagging_taggeditem
                                  WHERE (content_type_id = %s) and (tag_id = %s) 
                                )""" % (content_type, cat_tag_id))

  rows = cursor.fetchall()
  if(rows == None): rows = "error"
  cursor.close()
  return rows

#----------------------------------------------------------------------------------------------------------

def add_category(parent, name):
  if settings.DATABASE_ENGINE != 'mysql':
    return "error: xml-rpc not supported"
  if myConnection == None:
    return "error: no connection with db server"

  cursor = myConnection.cursor()

  cursor.execute("SELECT id FROM wiki_wikicategory WHERE (title = '%s')" % parent)    
  row = cursor.fetchone()
  if row == None:
    return "error: parent category does not exists"

  cursor.execute("SELECT id FROM tagging_tag WHERE (name = '%s')" % parent)    
  row = cursor.fetchone()
  if row == None:
    return "error: parent category does not exists"

  parent_id = str(row[0])

  cursor.execute("SELECT * FROM wiki_wikicategory WHERE (title = '%s')" % name)    
  row = cursor.fetchone()
  if row != None:
    return "error: category with this '%s' already exists" % name

  cursor.execute("INSERT INTO wiki_wikicategory (title, tags) VALUES ('%s', '')" % name)      
  cat_id =  str(myConnection.insert_id())

  cursor.execute("SELECT id FROM tagging_tag WHERE name = '%s'" % name)    
  row = cursor.fetchone()
  if row == None:
    cursor.execute("INSERT INTO tagging_tag (name) VALUES('%s')" % name)    
    cat_tag_id = str(myConnection.insert_id())
  else:
    cat_tag_id = str(row[0])

  cursor.execute("SELECT id FROM django_content_type WHERE (model = 'wikicategory')")    
  row = cursor.fetchone()
  if row == None:
    cursor.close()
    return "error"

  content_type = row[0]

  cursor.execute("""INSERT INTO tagging_taggeditem (tag_id, content_type_id, object_id) 
                    VALUES (%s, %s, %s)""" % (parent_id, content_type, cat_id))    

  cursor.close()
  myConnection.commit()
  return ""


#----------------------------------------------------------------------------------------------------------
 
dispatcher.register_function(update_page, 'update_page')
dispatcher.register_function(create_page, 'create_page')
dispatcher.register_function(get_page_list, 'get_page_list')
dispatcher.register_function(get_page, 'get_page')
dispatcher.register_function(get_revision, 'get_revision')
dispatcher.register_function(get_category, 'get_category')
dispatcher.register_function(add_category, 'add_category')