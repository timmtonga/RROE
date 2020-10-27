import json
from couchdb import Server


config_file = "config/application.config"
settings = {}

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))

# Connect to a database or Create a Database
db_name = settings["couch"]["database"] + "_patients"

try:
    db = couchConnection[db_name]
except:
    db = couchConnection.create(db_name)


def archive_records():
    for i in range(1, 70):
        records = db.find({"selector": {"type": {"$ne": "patient"}}, "limit": 100})
        db.purge(records)


if __name__ == '__main__':
    archive_records()
