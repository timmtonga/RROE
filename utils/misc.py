#this is a a location for all the miscileneous functions
from datetime import date
import json

#calculate age for display
def calculate_age(birth_date):
    age_in_days = int((date.today() - birth_date).days)

    if age_in_days < 31:
      return str(age_in_days) + " days"
    elif age_in_days < 548:
      years = int(date.today().year - birth_date.year)
      months = int(date.today().month - birth_date.month)
      return str((years * 12) + months) + " months"
    else:
      return str(int(age_in_days / 365.2425)) + " years"


def collapse_test_orders(orders):
    if (("Full Blood Count" in orders) and ("Malaria Screening" in orders)):
        pass
        #pop those two out and combine them in one
    pass

def initialize_settings():
    settings = {}
    try:
        with open("config/application.config") as json_file:
            settings = json.load(json_file)
    except:
        pass
    return settings

def current_facility():
    try:
        with open("config/application.config") as json_file:
            return json.load(json_file)["facility"]
    except:
        return "Undefined"

def container_options():
    return {"containers": {'Sterile container': "blue_top_urine.png",
                           'Red top': "red_top.jpg", 'Baktech':"bactec.png",
                           'Conical container': "conical_contatiner.jpeg",
            'EDTA': 'purple_top.jpg', 'yellow top': "yellow_top.jpg"}}
