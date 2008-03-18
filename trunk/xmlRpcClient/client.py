import sys
import xmlrpclib

rpc_srv = xmlrpclib.ServerProxy("http://localhost:8000/xmlrpc/")

#print rpc_srv.create_page("hello", "hello", "rpc-bot", "wikimedia", "rpc test")
#print rpc_srv.update_page("test1", "test hello", "rpc-bot", "wikimedia", "basic test rpc")
#print rpc_srv.get_revision("test1", 1)
#print rpc_srv.get_category("cat1")
print rpc_srv.add_category("cat1", "rpc3")




