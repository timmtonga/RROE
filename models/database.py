from utils import misc
from couchdb import Server


class DataAccess:
    def __init__(self, database=None):
        # Main application configuration
        settings = misc.initialize_settings()

        # Connect to a couchdb instance
        couch_connection = Server("http://%s:%s@%s:%s/" %
                                  (settings["couch"]["user"], settings["couch"]["passwd"],
                                   settings["couch"]["host"], settings["couch"]["port"]))

        # Connect to a database or Create a Database
        db_name = settings["couch"]["database"] if database is None else settings["couch"]["database"] + "_" + database
        try:
            self.db = couch_connection[db_name]
        except:
            self.db = couch_connection.create(db_name)
