import sys
import xmlrpclib

selecttext = """SELECT * FROM wiki_wikipagetitle WHERE id = 6"""

updatetext = """
UPDATE wiki_wikipagetitle SET title = 'home' WHERE id = 1
"""
insertTitleText = """
REPLACE INTO wiki_wikipagetitle VALUES(2, 'xmlrpc', 0)
"""
insertContentText = """
REPLACE INTO wiki_wikipagecontent 
VALUES(2, 2, 'This page was added via xml-rpc. Hello Again!', 'ALeRT', 0, '2008-03-05 23:30:11.500000', 'markdown', '')
"""

text = """
INSERT INTO wiki_wikipagetitle VALUES(6, 'xmlrpc', 0);
SELECT * FROM wiki_wikipagetitle WHERE id = 6;
"""


rpc_srv = xmlrpclib.ServerProxy("http://localhost:8000/xmlrpc/")

rpc_srv.execsql([insertTitleText, insertContentText])



