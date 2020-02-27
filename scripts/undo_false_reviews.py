import csv
import json
from couchdb import Server
from couchdb.design import ViewDefinition
from werkzeug.security import generate_password_hash

global db


print("Initializing")
try:
    config_file = "config/application.config"
    settings = {}
    with open(config_file) as json_file:
        settings = json.load(json_file)
except IOError:
    print("File not accessible")


couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))

#del couchConnection[settings["couch"]["database"]]

global db
# Connect to a database or Create a Database
try:
    db = couchConnection[settings["couch"]["database"]]
except:
    db = couchConnection.create(settings["couch"]["database"])

tests = db.find({"selector": {"status": "Specimen Rejected","type": {"$in": ["test","test panel"]}}, "limit": 100})
i= 0
for test in tests:
    if (test.get("measures") != None):
        test["status"] = "Analysis Complete"
        db.save(test)
        print(test["_id"])
        i+=1

print("Affected tests " + str(i))

