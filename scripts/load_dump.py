from couchdb import Server  # importing couchdb
import json

config_file = "config/application.config"
settings = {}

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"], settings["couch"]["passwd"],
                          settings["couch"]["host"], settings["couch"]["port"]))

# Connect to a database or Create a Database
try:
    db = couchConnection[settings["couch"]["database"]]
except:
    db = couchConnection.create(settings["couch"]["database"])


def initialize_restore():
    print("Begin restoration")
    data = {}
    with open("db.json") as json_file:
        data = json.load(json_file)
    for i in data["rows"]:
        rec = i["doc"]
        rec.pop("_rev")
        db.save(rec)

if __name__ == '__main__':
    initialize_restore()
