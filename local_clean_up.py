import json
import datetime
from models.patient import Patient
from models.database import DataAccess


def initiate_archiving():
    print("Beginning archiving records")
    patient_ids = DataAccess("patients").db.find({"selector": {"_id": {"$gt": None}}, "fields": ["_id"], "limit": 9000})

    # get all patient ids
    for row in patient_ids:
        test_records = DataAccess().db.find({"selector": {"patient_id": row["_id"]}, "limit": 9000})

        if len(test_records) > 0:
            # Check patient record for last test
            archive_record = check_recent_test(test_records)

            if archive_record:
                archive_records(test_records)


def archive_records(records):
    backup_name = "records_archive.json"
    file1 = open(backup_name, "a")
    for record in records:
        file1.write(json.dumps(record))

    file1.close()
    DataAccess().db.purge(records)


def check_recent_test(records):
    current_time = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%s')

    for i in records:
        if float(i["date_ordered"]) >= float(current_time):
            return False
    return True


if __name__ == '__main__':
    initiate_archiving()
