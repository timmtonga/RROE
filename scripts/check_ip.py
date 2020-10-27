import json
from couchdb import Server
import os

replications_file = "config/replications.config"
config_file = "config/application.config"
settings = {}

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))

ip_address = os.popen("hostname -I").read().strip()
new_ip_address = "http://%s:%s/%s" % ('localhost', settings["couch"]["port"], settings["couch"]["database"])

with open(replications_file, "r") as replications:
    for destination in replications:
        print(destination)
        print(new_ip_address)
        couchConnection.replicate(destination, new_ip_address, continuous=True)
        couchConnection.replicate(new_ip_address, destination, continuous=True)
