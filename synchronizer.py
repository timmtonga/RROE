import os
import json
import mysql.connector
from couchdb import Server
from datetime import datetime
test_statuses = {1:"Specimen Received",2:"Specimen Received",
                 3:"Being Analyzed",4:"Pending Verification",5:"Analysis Complete",6:"Not Done",7:"Not Done",8:"Rejected"}

config_file = "config/application.config"
settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

global db
global mysqldb

def check_pending():
    log("Check begun at %s" % datetime.utcnow().strftime("%d/%m/%Y %H:%S"))
    connect_to_couch()
    pending_tests = db.find({
            "selector": {
                "type": "test",
                "status": {"$in": ["Ordered", "Specimen Collected", "Specimen Received", "Being Analyzed","Pending Verification"]}
            }
    })
    connect_to_blis()
    for test in pending_tests:
        myTest = None
        mycursor = mysqldb.cursor()
        #Does test have test has accession number or lims id?
        #if no
        if test.get("lims_id") == None:
            #get patient_id
            mycursor.execute("SELECT id FROM patients where external_patient_number = '%s' order by id desc" % test["patient_id"] )
            mypatient = mycursor.fetchone()
            if mypatient == None:
                next
            else:
                patient_id = mypatient[0]
                #get last test for patient with that id.
                query = "SELECT id, test_status_id from tests where test_type_id = "+test.get("test_type")+" and requested_by = '"+test.get("ordered_by") +"' and visit_id in (select id from visits where patient_id = "+str(patient_id)+" and created_at between '"+datetime.utcfromtimestamp(float(test.get("date_ordered"))).strftime("%Y-%m-%d %H:%M")+"' and now()) order by id desc"
                mycursor.execute(query)
                myTest = mycursor.fetchone()
                test["lims_id"] = myTest[0]
        else:
            #if test has accession number
            query = "SELECT id, test_status_id from tests where id = %s" % test.get("lims_id")
            mycursor.execute(query)
            myTest = mycursor.fetchone()

        if myTest == None:
            pass
        else:
            #check if status is different from what is known
            if test.get("status") != test_statuses[myTest[1]]:
                #Test has different state? update status
                test["status"] = test_statuses[myTest[1]]

                # test authorized? yes, get result
                if test_statuses[myTest[1]] == "Analysis Complete":
                    test["measures"] = {}

                    mycursor.execute("SELECT (SELECT `name` FROM measures where id = measure_id) as measure, result FROM test_results where test_id = %s" % myTest[0])
                    measures= mycursor.fetchall()
                    for measure in measures:
                        test["measures"][measure[0]] = measure[1]
        db.save(test)
    log("Check concluded at %s" % datetime.utcnow().strftime("%d/%m/%Y %H:%S"))

def connect_to_couch():
    couchConnection = Server("http://%s:%s@%s:%s/" %
                                 (settings["couch"]["user"],settings["couch"]["passwd"],
                                  settings["couch"]["host"],settings["couch"]["port"]))
    # Connect to a database or Create a Database
    global db
    try:
       db = couchConnection[settings["couch"]["database"]]
    except:
        db = couchConnection.create(settings["couch"]["database"])

def connect_to_blis():
    global mysqldb
    mysqldb = mysql.connector.connect(host=settings["iblis"]["host"],user=settings["iblis"]["user"],passwd=settings["iblis"]["password"],database=settings["iblis"]["database"])

def log(message):
    f = open("synchronization.log", "a+")
    f.write("%s \n" % message)
    f.close()

if __name__ =='__main__':
    check_pending()
