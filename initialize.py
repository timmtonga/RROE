import os
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
        db.save(test_options[test_details])
        #db.save(test)

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
