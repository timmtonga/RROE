# this is a a location for all the miscellaneous functions
from datetime import date
import json


# calculate age for display

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
    collapsed_orders = []
    tests_by_depts = {}
    for order in orders:
        if order.get("type") == "test panel":
            collapsed_orders.append(order)
        else:
            if tests_by_depts.get(order.get("department")) is None:
                tests_by_depts[order.get("department")] = {order.get("specimen_type"): []}
            try:
                tests_by_depts[order.get("department")][order.get("specimen_type")].append(order)
            finally:
                pass

    for dept in tests_by_depts.keys():
        for specimen_type in tests_by_depts[dept].keys():
            if len(tests_by_depts[dept][specimen_type]) == 1:
                collapsed_orders.append(tests_by_depts[dept][specimen_type][0])
            else:
                collapsed_orders += ([tests_by_depts[dept][specimen_type][i * 3:(i + 1) * 3] for i in
                                      range((len(tests_by_depts[dept][specimen_type]) + 3 - 1) // 3)])

    return collapsed_orders


def initialize_settings():
    settings = {}
    try:
        with open("config/application.config") as json_file:
            settings = json.load(json_file)
    finally:
        pass
    return settings


def current_facility():
    try:
        with open("config/application.config") as json_file:
            settings = json.load(json_file)
            return settings["facility"]
    except:
        return "Undefined"


def container_options():
    return {'Sterile container': "blue_top_urine.png", "Swab": "swab.jpg",
            'Red top': "red_top.jpg", 'Baktech': "bactec.png",
            'Conical container': "conical_contatiner.jpeg",
            'EDTA': 'purple_top.jpg', 'yellow top': "yellow_top.jpg"}
