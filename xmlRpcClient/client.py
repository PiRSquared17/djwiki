import sys
import xmlrpclib

rpc_srv = xmlrpclib.ServerProxy("http://localhost:8000/xmlrpc/?u=admin&p=qqq")

#print rpc_srv.create_page("hello", "hello", "rpc-bot", "wikimedia", "rpc test")
#print rpc_srv.update_page("test1", "test hello", "rpc-bot", "wikimedia", "basic test rpc")
print rpc_srv.get_revision("home", 0)
#print rpc_srv.get_category("Main")
#print rpc_srv.add_category("cat1", "rpc3")




