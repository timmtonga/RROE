from models.database import DataAccess


class LaboratoryTestPanel:
    def __init__(self, name, short_name, tests, panel_id, spec_types, orderable=True, available=True):
        self.database = DataAccess("lab_test_panels").db
        self.tests = tests
        self.panel_name = name
        self.panel_id = panel_id
        self.available = available
        self.orderable = orderable
        self.short_name = short_name
        self.specimen_types = spec_types

    @staticmethod
    def get(panel_id):
        panel = DataAccess("lab_test_panels").db.get(panel_id)
        if panel is not None:
            availability = panel.get("availability") if panel.get("availability") is not None else True
            panel = LaboratoryTestPanel(panel["_id"], panel["short_name"], panel["tests"], panel["panel_id"],
                                       panel["specimen_types"], panel["orderable"], availability)

        return panel

    @staticmethod
    def get_available():
        tests = DataAccess("lab_test_panels").db.find({"selector": {"availability": True}, "limit": 5000})
        return tests

    def show(self):
        return self.__str__()

    def save(self):
        panel = self.database.get(self.panel_name)

        if panel is None:
            panel = self.__repr__()

        self.database.save(panel)

    def __str__(self):
        return 'TestPanel(panel_name: '+self.panel_name + ', short_name: '+self.short_name + ', panel_id: ' + \
               self.panel_id + ', specimen_types: '+self.specimen_types + ', tests: '+self.tests +\
               ', orderable: '+self.orderable + ', availability: '+self.available+')'

    def __repr__(self):
        return {'_id': self.panel_name, 'short_name': self.short_name, 'panel_id': self.panel_id,
                'specimen_types': self.specimen_types, 'tests': self.tests, 'availability': self.available,
                'orderable': self.orderable, 'type': 'Laboratory Test Panel'}
