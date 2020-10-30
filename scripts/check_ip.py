import json
from couchdb import Server
# import os

replications_file = "config/replications.config"
config_file = "config/application.config"
settings = {}

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"], settings["couch"]["passwd"],
                          settings["couch"]["host"], settings["couch"]["port"]))

# ip_address = os.popen("hostname -I").read().strip()
new_ip_address = "http://%s:%s@%s:%s/%s" % (settings["couch"]["user"], settings["couch"]["passwd"],
                                            'localhost', settings["couch"]["port"], settings["couch"]["database"])

with open(replications_file, "r") as replications:
    sub_directories = ["", "_lab_test_panels", "_lab_test_type", "_patients", "_users"]
    for destination in replications:
        for sub_dir in sub_directories:
            couchConnection.replicate(new_ip_address + sub_dir, destination + sub_dir, continuous=True)
            couchConnection.replicate(destination + sub_dir, new_ip_address + sub_dir, continuous=True)

