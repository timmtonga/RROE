import json
import mysql.connector
from couchdb import Server
from datetime import datetime, timedelta
from models.laboratory_test_type import LaboratoryTestType
from models.laboratory_test_panel import LaboratoryTestPanel

test_statuses = {1: "Specimen Received", 2: "Specimen Received", 3: "Being Analyzed", 4: "Pending Verification",
                 5: "Analysis Complete", 6: "Not Done", 7: "Not Done", 8: "Rejected"}

config_file = "config/application.config"
settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

global db
global mysqldb


def sync_test_statuses():
    log("Check begun at %s" % datetime.now().strftime("%d/%m/%Y %H:%S"))
    print("Check begun at %s" % datetime.now().strftime("%d/%m/%Y %H:%S"))
    pending_tests = get_pending_tests()

    # Have items that need updating
    if len(pending_tests) > 0:
        connect_to_blis()

    for test in pending_tests:
        updated_test = process_test(test)
        if updated_test is not None:
            try:
                db.save(updated_test)
            except:
                pass

    pending_panels = get_pending_panels()

    for panel in pending_panels:
        processed_panel = process_panel(panel)
        try:
            db.save(processed_panel)
        except:
            pass

    log("Check concluded at %s" % datetime.now().strftime("%d/%m/%Y %H:%S"))
    print("Check concluded at %s" % datetime.now().strftime("%d/%m/%Y %H:%S"))


def get_pending_tests():
    tests = db.find({
            "selector": {
                "type": "test",
                "status": {"$in": ["Ordered", "Specimen Collected", "Specimen Received", "Being Analyzed",
                                   "Pending Verification"]}}, "limit": 1000
    })
    return tests


def get_pending_panels():
    return db.find({
            "selector": {
                "type": "test panel",
                "status": {"$in": ["Ordered", "Specimen Collected", "Specimen Received", "Being Analyzed",
                                   "Pending Verification"]}
            }, "limit": 1000})


def get_patient_id(npid):
    # Get patient id from blis

    cursor = mysqldb.cursor()
    cursor.execute("SELECT id FROM patients where external_patient_number = '%s' order by id desc LIMIT 1" % npid)
    patient_records = cursor.fetchone()
    if patient_records is None:
        return None
    else:
        return patient_records[0]


def get_patient_test(patient_id, test_type_id, ordered_by, ordered_on):
    my_cursor = mysqldb.cursor()
    query = "SELECT id, test_status_id,not_done_reasons,specimen_id from tests where test_type_id = "+test_type_id+\
            " and requested_by = '"+ordered_by + "' and visit_id in (select id from visits where patient_id = "+\
            str(patient_id)+" and created_at between '"+\
            (datetime.fromtimestamp(float(ordered_on)) - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")+"' and now()) order by id desc LIMIT 1"
    my_cursor.execute(query)
    my_test = my_cursor.fetchone()
    if my_test is None:
        return None
    else:
        return my_test


def get_test(test_id):
    my_cursor = mysqldb.cursor()
    query = "SELECT id, test_status_id,not_done_reasons,specimen_id from tests where id = %s" % test_id
    my_cursor.execute(query)
    my_test = my_cursor.fetchone()
    if my_test is None:
        return None
    else:
        return my_test


def update_test_status(test, test_details):
    # Test has different state? update status
    old_test = test
    test["status"] = test_statuses[test_details[1]]

    if test_details[1] == 7:
        # Test not done
        mycursor = mysqldb.cursor()
        mycursor.execute("SELECT reason from not_done_reasons where id = %s" % test_details[2])
        reason= mycursor.fetchone()
        test["rejection_reason"] = reason[0]
    elif test_details[1] == 8:
        # test rejected
        mycursor = mysqldb.cursor()
        mycursor.execute("SELECT reason from rejection_reasons WHERE id = " +
                         "(select rejection_reason_id from specimens where id = %s)" % test_details[3])
        reason= mycursor.fetchone()
        test["rejection_reason"] = reason[0]
    elif test_statuses[test_details[1]] == "Analysis Complete":
        # test authorized? yes, get results
        test["measures"] = {}
        mycursor = mysqldb.cursor()
        mycursor.execute("SELECT (SELECT `name` FROM measures where id = measure_id) as measure, result " +
                         "FROM test_results where test_id = %s" % test_details[0])
        measures= mycursor.fetchall()
        for measure in measures:
            test["measures"][measure[0]] = measure[1]

    return test


def connect_to_couch():
    couchConnection = Server("http://%s:%s@%s:%s/" % (settings["couch"]["user"], settings["couch"]["passwd"],
                                                      settings["couch"]["host"], settings["couch"]["port"]))
    # Connect to a database or Create a Database
    global db
    try:
       db = couchConnection[settings["couch"]["database"]]
    except:
       db = couchConnection.create(settings["couch"]["database"])


def connect_to_blis():
    global mysqldb
    mysqldb = mysql.connector.connect(host=settings["iblis"]["host"], user=settings["iblis"]["user"],
                                      passwd=settings["iblis"]["password"], database=settings["iblis"]["database"])


def log(message):
    f = open("synchronization.log", "a+")
    f.write("%s \n" % message)
    f.close()


def process_test(test):
    if test.get("lims_id") is None:
        # get patient_id in lims
        patient_id = get_patient_id(test["patient_id"])
        if patient_id is None:
            log("Couldn't find patient with id %s" % test["patient_id"])
            return None
        else:
            # get last test for patient with that id.
            test_details = get_patient_test(patient_id,test.get("test_type"),test.get("ordered_by"),
                                            test.get("date_ordered"))

            if test_details is None:
                log("Couldn't find test for patient with id %s and test type %s ordered on %s" %
                    (test["patient_id"], test.get("test_type"),
                     datetime.fromtimestamp(float(test.get('date_ordered'))).strftime('%d %b %Y %H:%S')))
                return None
            else:
                test["lims_id"] = test_details[0]
    else:
        # if test has lims id
        test_details = get_test(test.get("lims_id"))

    if test_details is None:
            log("Couldn't find test for patient with id %s and test id %s" % (test["patient_id"], test.get("lims_id")))
            return
    else:
        if test.get("status") != test_statuses[test_details[1]]:
            updated_test = update_test_status(test, test_details)
            return updated_test


def process_panel(panel):
    patient_id = None

    if not panel.get("tests").keys():
        panel_details = LaboratoryTestPanel.get(panel["panel_type"])
        if panel_details is not None:
            for test_in_panel in panel_details.tests:
                panel['tests'][LaboratoryTestType.get(test_in_panel).test_type_id] = {}

    for test_type_id in panel.get("tests").keys():
        test = panel.get("tests")[test_type_id]
        test_details = None
        if test.get("lims_id") is None:
            # get patient_id in lims
            if patient_id is None:
                result = get_patient_id(panel["patient_id"])
                if result is None:
                    log("Couldn't find patient with id %s" % panel["patient_id"])
                    return panel
                patient_id = result

            # get last test for patient with that id
            test_details = get_patient_test(patient_id,test_type_id,panel.get("ordered_by"), panel.get("date_ordered"))
        else:
            # if test has lims id
            test_details = get_test(test.get("lims_id"))

        if test_details is None:
            log("Couldn't find test for patient with id %s and panel test type %s ordered on %s" %
                (panel["patient_id"], test_type_id, panel.get("date_ordered")))
        else:
            print("Found test for patient with id %s and panel test type %s ordered on %s" %
                  (panel["patient_id"], test_type_id, panel.get("date_ordered")))
            if test.get("lims_id") is None:
                test["lims_id"] = test_details[0]

            if test.get("status") is None or test.get("status") != test_statuses[test_details[1]]:
                updated_test = update_test_status(test, test_details)
                panel["tests"][test_type_id] = updated_test
                if panel["status"] != "Analysis Complete":
                    panel["status"] = test.get("status")
    return panel


if __name__ == '__main__':
    connect_to_couch()
    sync_test_statuses()

