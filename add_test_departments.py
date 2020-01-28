import csv
import json
from couchdb import Server

config_file = "config/application.config"
settings = {}
try:
    with open(config_file) as json_file:
        settings = json.load(json_file)
except IOError:
    print("File not accessible")

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))

db = couchConnection[settings["couch"]["database"]]

with open('test_departments.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                record = db.get(row[1])
                if record != None:
                    record["department"] = row[3]
                    db.save(record)

