from models.laboratory_test_type import LaboratoryTestType
from models.laboratory_test_panel import LaboratoryTestPanel

new_test = LaboratoryTestType.get("Manual Differential & Cell Morphology")

if new_test is None:
    new_test = LaboratoryTestType("Manual Differential & Cell Morphology",
                                  {"3": {"volume": "3", "units": "ml", "container": "EDTA", "type_of_specimen": "Blood"}},
                                  "PRSM", "45", {
                                      "RBC Comments": {"type": "Free Text"}, "WBC Comments": {"type": "Free Text"},
                                      "Interpretative Comments": {"type": "Free Text"},
                                      "Attempted/ Differential Diagnosis": {"type": "Free Text"},
                                      "Further Tests": {"type": "Free Text"}
                                  }, {"3": "Blood"}, "Haematology", True)
else:
    new_test.specimen_requirements = {"3": {"volume": "3", "units": "ml", "container": "EDTA",
                                         "type_of_specimen": "Blood"}}
    new_test.short_name = "PRSM"
    new_test.test_type_id = "45"
    new_test.measures = {"RBC Comments": {"type": "Free Text"}, "WBC Comments": {"type": "Free Text"},
                         "Interpretative Comments": {"type": "Free Text"},
                         "Attempted/ Differential Diagnosis": {"type": "Free Text"},
                         "Further Tests": {"type": "Free Text"}}
    new_test.specimen_requirements = {"3": "Blood"}
    new_test.department = "Haematology"
    new_test.available = True

new_panel = LaboratoryTestPanel("PBF", "PBF", ["Manual Differential & Cell Morphology", "FBC"], None, {"3": "Blood"},
                                False, True)

new_test.save()
new_panel.save()
