from models.database import DataAccess


class LaboratoryTestType:
    def __init__(self, name, spec_req, short_name, test_type, measures, spec_types, department, available=True, ver=''):
        self.database = DataAccess("lab_test_type").db
        self.test_name = name
        self.measures = measures
        self.available = available
        self.department = department
        self.short_name = short_name
        self.test_type_id = test_type
        self.specimen_types = spec_types
        self.specimen_requirements = spec_req
        self.revision = ver

    @staticmethod
    def get(test_id):
        test_type = DataAccess("lab_test_type").db.get(test_id)
        if test_type is not None:
            availability = test_type.get("availability") if test_type.get("availability") is not None else True
            test_type = LaboratoryTestType(test_type["_id"], test_type["requirements"],
                                           test_type["short_name"], test_type["test_type_id"], test_type["measures"],
                                           test_type["specimen_types"], test_type["department"], availability,
                                           test_type["_rev"])

        return test_type

    @staticmethod
    def find_by_test_type(test_type_id):
        test_type = DataAccess("lab_test_type").db.find({"selector": {"test_type_id": test_type_id}, "limit": 1})
        if test_type is not None:
            test_type = test_type[0]
            availability = test_type.get("availability") if test_type.get("availability") is not None else True
            test_type = LaboratoryTestType(test_type["_id"], test_type["requirements"],
                                           test_type["short_name"], test_type["test_type_id"], test_type["measures"],
                                           test_type["specimen_types"], test_type["department"], availability)

        return test_type

    @staticmethod
    def find_by_test_types(test_types):
        return DataAccess("lab_test_type").db.find({"selector": {"_id": {"$in": test_types}}})

    @staticmethod
    def match_specimen_types(spec_type):
        test_types = DataAccess("lab_test_type").db.find({"selector": {"_id": {"$gt": None}}})
        for i in test_types:
            for t in i["specimen_types"]:
                if spec_type == t:
                    return i["specimen_types"][t]

    @staticmethod
    def get_specimen_types():
        test_types = DataAccess("lab_test_type").db.find({"selector": {"_id": {"$gt": None}}})
        options = []
        for i in test_types:
            for t in i["specimen_types"]:
                if [i["specimen_types"][t], t] not in options:
                    options.append([i["specimen_types"][t], t])

        return options

    @staticmethod
    def get_available():
        tests = DataAccess("lab_test_type").db.find({"selector": {"availability": True}, "limit": 5000})
        return tests

    def show(self):
        return self.__str__()

    def save(self):
        test_type = self.database.get(self.test_name)

        if test_type is None:
            test_type = self.__repr__()
            test_type.pop("_rev")
        else:
            test_type = self.__repr__()

        self.database.save(test_type)

    def printable_name(self):
        return self.short_name if self.short_name != "" else self.test_name

    def __str__(self):
        return 'LaboratoryTestType(test_name: '+self.test_name + ', short_name: '+self.short_name + ', department: ' + \
               self.department + ', test_type_id: '+self.test_type_id + ', specimen_types: '+self.specimen_types + \
               + ', measures: '+self.measures + ', requirements: '+self.specimen_requirements +  \
               ', availability: '+str(self.available)+')'

    def __repr__(self):
        return {'_id': self.test_name, 'short_name': self.short_name, 'department': self.department,
                'test_type_id': self.test_type_id, 'specimen_types': self.specimen_types, 'measures': self.measures,
                'requirements': self.specimen_requirements, 'availability': self.available,
                '_rev': self.revision, 'type': 'Laboratory Test'}
