import csv
import json
from couchdb import Server

settings = {}
specimen_types = {"1":"Sputum","2":"CSF","3":"Blood","4":"Pleural Fluid","5":"Ascitic Fluid","6":"Pericardial Fluid",
                  "7":"Peritoneal Fluid","8":"HVS","9":"Swabs","10":"Pus","11":"Stool","12":"Urine","13":"Other","15":"Semen",
                  "16":"Swab","17":"Synovial Fluid","18":"Plasma","22":" tissue biopsy"}

config_file = "config/application.config"

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                                 (settings["couch"]["user"],settings["couch"]["passwd"],
                                  settings["couch"]["host"],settings["couch"]["port"]))
# Connect to a database or Create a Database
global db
try:
   db = couchConnection[settings["couch"]["database"]]
except:
    db = couchConnection.create(settings["couch"]["database"])


with open('test_panels.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            line_count += 1
            panel = {"_id" : row[1], "specimen_types": {}, "orderable":True, "tests":[], "type":"panels", "panel_id": row[0], "short_name":row[2]}
            if row[5] == "0":
                panel["orderable"] = False
                panel["panel_id"] = None

            for i in row[4].split("|"):
                panel["specimen_types"][i] = specimen_types[i]

            for i in row[3].split("|"):
                test_name = db.find({  "selector": {"type": "test_type","test_type_id": i },"fields": ["_id"], "limit": 1})
                panel["tests"].append(test_name[0]["_id"])

            db.save(panel)

