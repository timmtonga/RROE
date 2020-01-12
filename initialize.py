import os
import csv
import json
from couchdb import Server
from couchdb.design import ViewDefinition

global db

def initialize():
    print("Initializing")
    try:
        config_file = "config/application.config"
        settings = {}
        with open(config_file) as json_file:
            settings = json.load(json_file)
    except IOError:
        print("File not accessible")
        return

    couchConnection = Server("http://%s:%s@%s:%s/" %
                             (settings["couch"]["user"],settings["couch"]["passwd"],
                              settings["couch"]["host"],settings["couch"]["port"]))

    del couchConnection[settings["couch"]["database"]]

    global db
    # Connect to a database or Create a Database
    try:
        db = couchConnection[settings["couch"]["database"]]
    except:
        db = couchConnection.create(settings["couch"]["database"])

    initialize_tests()
    initialize_views()

def initialize_tests():
    print("Initializing tests")
    test_options = {}
    test_file = "test_details.json"
    with open(test_file) as json_file:
        specimen_types = json.load(json_file)

    for specimen_type, tests in specimen_types.items():
        for test_name, test in tests['tests'].items():
            if test_options.get(test.get("test_type_id")) == None:
                test_options[test.get("test_type_id")] =  {"_id": test_name, "test_type_id" : test.get("test_type_id"), "measures": test.get("measures"), "type": "test_type" }
                if test.get("short_name") != None:
                    test_options[test.get("test_type_id")]['short_name'] = test.get("short_name")

            if ( test_options[test.get("test_type_id")].get("specimen_types")  == None ):
                test_options[test.get("test_type_id")]["specimen_types"] = {tests.get('specimen_type_id') : specimen_type}
            elif test_options[test.get("test_type_id")]["specimen_types"].get(tests.get('specimen_type_id')) == None:
                test_options[test.get("test_type_id")]["specimen_types"][tests.get('specimen_type_id')] = specimen_type

    for test_details in test_options:
        record = db.get(test_options[test_details]["_id"])
        if record == None:
            db.save(test_options[test_details])
        else:
            for key in test_options[test_details].keys():
                record[key] = test_options[test_details][key]
            db.save(record)

    with open('test_type_details_edited.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                record = db.get(row[1])
                if record == None:
                    pass
                else:
                    if record.get("specimen_requirements") == None:
                        record["specimen_requirements"] = {}
                    record["specimen_requirements"][row[4]] ={"container" : row[7], "volume": row[6].split(" ")[0], "units" : row[6].split(" ")[1], "type_of_specimen": row[5]}
                    db.save(record)

def initialize_views():
    print("Initializing views")
    view = ViewDefinition('users', 'teams', '''function(doc) {
            if (doc.type && doc.type == 'user' && doc.team){
                    emit(doc.team, doc._id);  
                }
            }''')

    view.get_doc(db)
    # The view is not yet stored in the database, in fact, design doc doesn't
    # even exist yet. That can be fixed using the `sync` method:
    view.sync(db)

if __name__ == '__main__':
    initialize()
