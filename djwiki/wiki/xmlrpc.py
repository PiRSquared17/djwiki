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


# Create a Dispatcher; this handles the calls and translates info to function maps
dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None) # Python 2.5

try:
  myConnection = MySQLdb.connect(host = "localhost",
                                 port = int("3306"),
                                 user = "root",
                                 passwd = "qqq",
                                 db = "djwiki")
except MySQLdb.Error, e:
  myConnection = None
 

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


def update_page(title, content, author, markupType):
  if myConnection == None:
    return "error: no connection with db server"
  cursor = myConnection.cursor()
  cursor.execute("SELECT id, title, head_revision FROM wiki_wikipagetitle WHERE title = '%s'" % title)
  row = cursor.fetchone()
  if row == None:
    return "error: no such page"
  title_id = row[0]
  head_rev = row[2]
  cursor.execute("SELECT id, title_id, content, author, revision, modificationTime, markupType, tags FROM wiki_wikipagecontent WHERE (title_id = %s)and(revision = %s)" % (title_id, head_rev))
  row = cursor.fetchone()
  if row == None:
    return "error"
  old_id = row[0]
  new_rev = str(int(row[4]) + 1)
  tags = row[7]

  cursor.execute("UPDATE wiki_wikipagetitle SET head_revision = %s WHERE id = %s" % (new_rev, title_id))
  cursor.execute("""INSERT INTO wiki_wikipagecontent (title_id, content, author, revision, modificationTime, markupType, tags)
                    VALUES(%s, '%s', '%s', %s, '%s', '%s', '%s')  
                 """ %(title_id, content, author, new_rev, MySQLdb.times.format_TIMESTAMP(datetime.datetime.now()), markupType, tags))

  newcont_id = myConnection.insert_id()
  cursor.execute("SELECT tag_id FROM tagging_taggeditem WHERE (content_type_id = 12) and (object_id = %s)" % old_id)  
  rows = cursor.fetchall()

  for row in rows:
    tag_id = row[0]
    print "tag_id = %s" % tag_id
    cursor.execute("""INSERT INTO tagging_taggeditem (tag_id, content_type_id, object_id) 
                      VALUES (%s, 12, %s)""" % (tag_id, newcont_id))    
  cursor.close()
  myConnection.commit()
  return ""

def create_page(title, content, author, markupType):
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

  cursor.close()
  myConnection.commit()
  return ""

def get_page_list():
  if myConnection == None:
    return "error: no connection with db server"
  cursor = myConnection.cursor()
  cursor.execute("SELECT * FROM wiki_wikipagetitle")
  rows = cursor.fetchall()
  cursor.close()
  return rows

def get_page(title):
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

def get_revision(title, rev):
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

 
dispatcher.register_function(update_page, 'update_page')
dispatcher.register_function(create_page, 'create_page')
dispatcher.register_function(get_page_list, 'get_page_list')
dispatcher.register_function(get_page, 'get_page')
dispatcher.register_function(get_revision, 'get_revision')