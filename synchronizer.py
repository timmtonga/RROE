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

def sync_test_statuses():
    log("Check begun at %s" % datetime.utcnow().strftime("%d/%m/%Y %H:%S"))
    connect_to_couch()
    pending_tests = get_pending_tests()

    #Have items that need updating
    if len(pending_tests) > 0:
        connect_to_blis()

    for test in pending_tests:
        if test.get("lims_id") == None:
            #get patient_id in lims
            patient_id = get_patient_id(test["patient_id"])
            if patient_id == None:
                log("Couldn't find patient with id %s" % test["patient_id"])
                next
            else:
                #get last test for patient with that id.
                test_details = get_patient_test(patient_id,test.get("test_type"),test.get("ordered_by") ,test.get("date_ordered"))

                if test_details == None:
                    log("Couldn't find test for patient with id %s and test type %s ordered on %s" % (test["patient_id"], test.get("test_type"), test.get("date_ordered")))
                    next
                else:
                    test["lims_id"] = test_details[0]
        else:
            #if test has lims id
            test_details = get_test(test.get("lims_id"))
            if test_details == None:
                log("Couldn't find test for patient with id %s and test id %s" % (test["patient_id"], test.get("lims_id")))
                next

        if test.get("status") != test_statuses[test_details[1]]:
            update_test_status(test, test_details)

    pending_panels = get_pending_panels()

    for panel in pending_panels:
        pass
    log("Check concluded at %s" % datetime.utcnow().strftime("%d/%m/%Y %H:%S"))


def get_pending_tests():
    return db.find({
            "selector": {
                "type": "test",
                "status": {"$in": ["Ordered", "Specimen Collected", "Specimen Received", "Being Analyzed","Pending Verification"]}
            }
    })

def get_pending_panels():
    return db.find({
            "selector": {
                "type": "test panel",
                "status": {"$in": ["Ordered", "Specimen Collected", "Specimen Received", "Being Analyzed","Pending Verification"]}
            }})

def get_patient_id(npid):
    #Get patient id from blis
    mycursor = mysqldb.cursor()
    mycursor.execute("SELECT id FROM patients where external_patient_number = '%s' order by id desc" % npid)
    patient_records = mycursor.fetchone()
    if patient_records == None:
        return None
    else:
        return patient_records[0]

def get_patient_test(patient_id, test_type_id, ordered_by, ordered_on):
    mycursor = mysqldb.cursor()
    query = "SELECT id, test_status_id from tests where test_type_id = "+test_type_id+" and requested_by = '"+ordered_by +"' and visit_id in (select id from visits where patient_id = "+str(patient_id)+" and created_at between '"+datetime.utcfromtimestamp(float(ordered_on)).strftime("%Y-%m-%d %H:%M")+"' and now()) order by id desc"
    mycursor.execute(query)
    myTest = mycursor.fetchone()
    if myTest == None:
        return None
    else:
        return myTest

def get_test(test_id):
    mycursor = mysqldb.cursor()
    mycursor.execute("SELECT id, test_status_id from tests where id = %s" % test_id)
    myTest = mycursor.fetchone()
    if myTest == None:
        return None
    else:
        return myTest

def update_test_status(test, test_details):
    #Test has different state? update status
    test["status"] = test_statuses[test_details[1]]

    if test_details[1] == 7:
        #Test not done
        test["rejection_reason"] = ""
    elif test_details[1] == 8:
        #test rejected
        test["rejection_reason"] = ""
    elif test_statuses[test_details[1]] == "Analysis Complete":
        # test authorized? yes, get result
        test["measures"] = {}
        mycursor = mysqldb.cursor()
        mycursor.execute("SELECT (SELECT `name` FROM measures where id = measure_id) as measure, result FROM test_results where test_id = %s" % test_details[0])
        measures= mycursor.fetchall()
        for measure in measures:
            test["measures"][measure[0]] = measure[1]
    db.save(test)


def check_pending():

    for test in pending_tests:
        print(test["_id"])
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
                if myTest != None:
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
