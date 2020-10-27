from models.database import DataAccess


class LaboratoryTest:
    def __init__(self):
        self.database = DataAccess().db

    def get(self, test_id):
        test = self.database.find(test_id)
        return test


