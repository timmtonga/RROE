import json
from couchdb import Server
from models.user import User
from models.patient import Patient
from models.laboratory_test_type import LaboratoryTestType
from models.laboratory_test_panel import LaboratoryTestPanel


config_file = "config/application.config"
settings = {}

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))
# Connect to a database or Create a Database
db_name = settings["couch"]["database"]

try:
    db = couchConnection[db_name]
except:
    db = couchConnection.create(db_name)


def start():
    print("Starting")

    transfer_patient_demographics()
    transfer_users()
    transfer_test_types()
    transfer_test_panels()
    reformat_tests()

    print("Finished")


def transfer_patient_demographics():
    print("Beginning transfer of patient demographics")
    records = db.find({"selector": {"type": {"$eq": "patient"}}, "limit": 100000})

    for record in records:
        archived = False if record.get("archived") is None else True
        patient = Patient(record.get('_id'), record.get('name'), record.get('dob'), record.get('gender'), archived)
        patient.save()

    for i in range(1, 70):
        records = db.find({"selector": {"type": {"$eq": "patient"}}, "limit": 100})
        db.purge(records)


def transfer_users():
    print("Beginning transfer of user details")
    records = db.find({"selector": {"type": {"$eq": "user"}}, "limit": 100000})

    for record in records:
        user = User(record.get('_id'), record.get('name', "Unknown"), record.get('role'),
                    record.get('designation', 'Unassigned'), "", record.get('status', "Active"),
                    record.get('department', "Medical"), record.get('ward', None), record.get('team', "Unassigned"),
                    record.get("password_hash"))

        user.save()

    for i in range(1, 70):
        records = db.find({"selector": {"type": {"$eq": "user"}}, "limit": 100})
        db.purge(records)


def transfer_test_types():
    print("Beginning transfer of test types")
    records = db.find({"selector": {"type": {"$eq": "test_type"}}, "limit": 100000})

    for record in records:
        test_type = LaboratoryTestType(record.get("_id"), record.get("specimen_requirements"), record.get("short_name"),
                                       record.get('test_type_id'), record.get('measures'), record.get('specimen_types'),
                                       record.get('department'))
        test_type.save()

    for i in range(1, 10):
        records = db.find({"selector": {"type": {"$eq": "test_type"}}, "limit": 100})
        db.purge(records)


def transfer_test_panels():
    print("Beginning transfer of panels")
    records = db.find({"selector": {"type": {"$eq": "panels"}}, "limit": 100000})

    for record in records:
        panel = LaboratoryTestPanel(record.get('_id'), record.get('short_name'), record.get('tests'),
                                    record.get('panel_id'), record.get('specimen_types'), record.get('orderable'))
        panel.save()

    for i in range(1, 10):
        records = db.find({"selector": {"type": {"$eq": "panels"}}, "limit": 100})
        db.purge(records)


def reformat_tests():
    print("Refactoring tests and test panels")
    records = db.find({"selector": {"type": {"$in": ["test", "test panel"]}}, "limit": 100000})
    temp_db = couchConnection.create("refactor_temp")

    for record in records:
        record["date_ordered"] = int(record["date_ordered"])
        if record.get("collected_at") is not None:
            record["collected_at"] = int(record["collected_at"])

        if record.get("reviewed_at") is not None:
            record["reviewed_at"] = int(record["reviewed_at"])
        record.pop("_rev")
        temp_db.save(record)


if __name__ == '__main__':
    start()

