from couchdb import Server # importing couchdb
from couchdb.design import ViewDefinition
import random
import json
import datetime
from werkzeug.security import generate_password_hash

config_file = "config/application.config"
settings = {}

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))

# Connect to a database or Create a Database
try:
    db = couchConnection[settings["couch"]["database"]]
except:
    db = couchConnection.create(settings["couch"]["database"])


def initializeArchive():
    print("Beginning Archive")
    # get patients
    current_patients = db.find({"selector": {"type": "patient"}, "limit": 20000})
    records_to_archive = []
    # check if patient has test in last 2 weeks
    for patient in current_patients:
        records = db.find({"selector": {"type": {"$in": ["test", "test panel"]}, "patient_id": patient["_id"]},
                           "fields": ["_id", "date_ordered"], "limit": 20000})
        archive_record = check_recent_test(records)

        if archive_record:
            records_to_archive.append(patient["_id"])

    archive_records(records_to_archive)


def check_recent_test(records):
    current_time = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%s')

    for i in records:
        if float(i["date_ordered"]) >= float(current_time):
            return False
    return True


def archive_records(ids):
    records = db.find({"selector": {"type": {"$in": ["test", "test panel"]}, "patient_id": {"$in": ids}}, "limit": 20000})
    backup_name = "%s_backup.json" % datetime.datetime.now().strftime('%s')
    file1 = open(backup_name, "a")
    for record in records:
        file1.write(json.dumps(record))
        db.delete(record)

    file1.close()

    patients = db.find({"selector": {"_id": {"$in": ids}}, "limit": 20000})
    for patient in patients:
        print("Archiving patient %s" % patient["_id"])
        patient["archived"] = "True"
        db.save(patient)


if __name__ == '__main__':
    initializeArchive()
