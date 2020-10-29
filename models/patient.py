import datetime
from models.database import DataAccess


def calculate_age(birth_date):
    birth_date = datetime.datetime.strptime(birth_date, "%d-%m-%Y").date()
    age_in_days = int((datetime.date.today() - birth_date).days)

    if age_in_days < 31:
        return str(age_in_days) + " days"
    elif age_in_days < 548:
        years = int(datetime.date.today().year - birth_date.year)
        months = int(datetime.date.today().month - birth_date.month)
        return str((years * 12) + months) + " months"
    else:
        return str(int(age_in_days / 365.2425)) + " years"


class Patient:
    def __init__(self, npid, name, dob, gender, archived=False,rev=''):
        self.database = DataAccess("patients").db
        self.patient_id = npid
        self.name = name
        self.dob = dob
        self.gender = gender
        self.archived = archived
        self.version = rev

    @staticmethod
    def get(npid):
        patient = DataAccess("patients").db.get(npid)
        if patient is not None:
            patient["gender"] = 'male' if patient.get('gender') == 'M' else 'female'
            patient["age"] = calculate_age(patient.get('dob'))
            patient["birth_date"] = datetime.datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y")
            patient["id"] = npid
        return patient

    def show(self):
        return self.__str__()

    def age(self):
        return calculate_age(self.dob)

    def formatted_gender(self):
        return 'male' if self.gender == 'M' else 'female'

    def formatted_birthday(self):
        return datetime.datetime.strptime(self.dob, "%d-%m-%Y").strftime("%d-%b-%Y")

    def save(self):
        patient = self.database.get(self.patient_id)

        if patient is None:
            patient = self.__repr__()
            patient.pop("_rev")
        else:
            patient['dob'] = self.dob
            patient['name'] = self.name
            patient['gender'] = self.gender

        self.database.save(patient)

    def __str__(self):
        return 'Patient(id: '+self.patient_id + ', name: '+self.name + ', dob: '+self.dob + ', gender: '+self.gender \
               + ', '+'archived: '+self.archived+')'

    def __repr__(self):
        return {'_id': self.patient_id, 'name': self.name, 'type': 'patient', 'dob': self.dob, 'gender': self.gender,
                'archived': self.archived, '_rev': self.version, 'type': 'patient'}
