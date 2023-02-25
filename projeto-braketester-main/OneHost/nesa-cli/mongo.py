import couchdb
import json

couch = couchdb.Server()

# connect to MongoDB
server = couchdb.Server('http://127.0.0.1:5984/_utils')
couch.resource.credentials = ("admin", "adminpw")
# Acess an existing database
db = couch['nmi-channel_']

for id in db:
	print(id)
	
for doc in db.find({"selector": {"_id": {"$gt":"" }}}):
    print(json.dumps(doc, indent=4, sort_keys=True))
   

