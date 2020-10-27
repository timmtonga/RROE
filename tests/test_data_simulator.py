from couchdb import Server # importing couchdb
from couchdb.design import ViewDefinition
import random
import json
import datetime
from werkzeug.security import generate_password_hash

config_file = "config/application.config"
settings = {}

with open(config_file) as json_file:
    settings = json.load(json_file)

couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))

# Connect to a database or Create a Database
try:
    db = couchConnection[settings["couch"]["database"]]
except:
    db = couchConnection.create(settings["couch"]["database"])

orderers = []
test_status = ["Ordered", "Being Analyzed","Pending Verification", "Analysis Complete", "Reviewed"]

designations = {'N' : 'Nurse', 'S': 'Sister-in-charge' , 'M': 'Matron',
                'I': 'Intern Medical Offcer','R': 'Registrar', 'C': 'Consultant'}

test_types = db.find({"selector": {"type": "test_type"}, "limit": 200})

names = ['Harry','Jeremiah','Alfonso','Marion','Douglas','Johnnie','Darlene','Martin','Mario','Lana','Pablo',
           'Estefana','Lewis','Maurine','Jaleesa','Moises','Trinh','Eliza','Felisa','Mignon','Rey','Theo','Ria',
           'Kassandra','Olene','Lahoma','Anjelica','Ehtel','Tanisha','Willette','Gail',"Denna","Mellissa","Bess",
           "Abigail","Alexandra","Alison","Amanda","Amelia","Amy","Andrea","Angela","Anna","Anne","Audrey","Ava",
           "Bella","Bernadette","Carol","Caroline","Carolyn","Chloe","Claire","Deirdre","Diana","Diane","Donna",
           "Dorothy","Elizabeth","Ella","Emily","Emma","Faith","Felicity","","Megan","Melanie","Michelle","Molly",
           "Natalie","Nicola","Olivia","Penelope","Pippa","Rachel","Rebecca","Rose","Ruth","Sally","Samantha","Sarah",
           "Sonia","Sophie","Stephanie","Sue","Theresa","Tracey","Una","Vanessa","Victoria","Virginia","Wanda","Adam",
           "Adrian","Alan","Alexander","Andrew","Anthony","Austin","Benjamin","Blake","Boris","Brandon","Brian",
           "Cameron","Carl","Charles","Christian","Christopher","Colin","Connor","Dan","David","Dominic","Dylan",
           "Edward","Eric","Evan","Frank","Gavin","Gordon","Harry", "Denise","Berneice","Arlie","Gaynelle",
           "Fidelia","Vanetta","Julie","Mary","Sherie","Keisha","Piedad", "Dina","Danna"]

surnames = ['Ball','Bell','Berry','Black','Blake','Bond','Bower','Brown','Buckland','Burgess','Butler','Cameron',
           'Campbell','Carr','Chapman','Churchill','Clark','Clarkson','Coleman','Cornish','Davidson','Davies',
           'Dickens','Dowd','Duncan','Dyer','Edmunds','Ellison','Ferguson','Fisher','Forsyth','Fraser','Gibson',
           'Gill','Glover','Graham','Grant','Gray','Greene','Hamilton','Hardacre','Harris','Hart','Hemmings',
           'Henderson','Hill','Hodges','Howard','Hudson','Hughes','Hunter','Ince','Jackson','James','Johnston','Jones',
           'Kelly','Kerr','King','Knox','Lambert','Langdon','Lawrence','Lee','Lewis','Lyman','MacDonald','Mackay',
           'Mackenzie','MacLeod','Manning','Marshall','Martin','Mathis','May','McDonald','McLean','McGrath','Gulley',
           'Conn','Ledbetter','Christiansen','Morrow','Suggs','Burris','Mortensen','Mccffrey','Bethel',
           'Bullard','Fallon','Winkler','Hoff','Dabney','Swain','Osburn','Truit','Hook','Trotter','Douglas','Bennett',
           'WESTBAY','WEPPLER','WAMBOLDT','WALDROOP','VONDRASEK','VLAHAKIS','VINSANT','VANO','VANDERWEELE','TUFARO',
           'TUCKERMAN','TRUEHEART','TRETTIN','STAVISH','STARIN','SOOKRAM','SONNENFEL',
           'Lambert','Hopkins','Blair','Black','Norman','Gomez','Shelton','Martin']


def intializeFacts():
    simulateProviders()
    simulatePatients()
    #initializeViews()

def simulateProviders():
    for i in range(1,20):
        role = random.choice('NNND')
        provider = {
                'type': 'user',
                'name' : names[random.randint(0, (len(names)-1))] + ' ' + surnames[random.randint(0, (len(surnames)-1))],
                'dob': datetime.datetime.strptime('{} {}'.format(random.randint(1, 366), random.randint(1930,2019)), '%j %Y').strftime("%d-%m-%Y"),
                'gender': random.choice('FM'), 'password_hash': generate_password_hash('letmein')
        }

        if (role == 'N'):
            provider['role']  = 'Nurse'
            provider['designation'] =  designations[random.choice('NNNNNSSM')]
        else:
            provider['role']  = 'Doctor'
            provider['designation'] = designations[random.choice('IIIIRRRC')]
            provider['team'] = random.choice("ABCD")

        provider["_id"] = provider["name"].split(" ")[1].lower()+provider["name"][0][0].lower()
        print("Username %s Role: %s" % (provider["_id"],provider['role']))
        db.save(provider)
        if role == 'D':
            orderers.append(provider['_id'])

def simulatePatients():
    for i in range(1,100):
        id = ''.join(random.choice('34679ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(6))
        dob = datetime.datetime.strptime('{} {}'.format(random.randint(1, 366), random.randint(1930,2019)), '%j %Y').strftime("%d-%m-%Y")
        # Creating document
        doc = {'_id': id, 'name': names[random.randint(0, (len(names)-1))] + ' ' + surnames[random.randint(0, (len(surnames)-1))],
                    'dob': dob, 'gender': random.choice('FM'), 'type': 'patient'}

        db.save(doc)
'''
        nTests = random.randint(0,10)

        for n in range(0,nTests) :
            pass
            test_id = random.randint(0,(len(test_types)-1))
            test = {
                'ordered_by': random.choice(orderers),
                'date_ordered': (datetime.datetime.now() - datetime.timedelta(days= random.randint(0,5))),
                'status': test_status[random.randint(0, (len(test_status)-1))],
                'test_type': test_types[test_id]["test_type_id"],
                'type': 'test',
                'ward': random.choice(['4A', '4B','MSS','MHDU']),
                'patient_id': id
            }

            if test['status'] == "Specimen Collected":
                #test["collected_by"] =
                test["collected_at"] = test["date_ordered"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["collected_at"] = test["collected_at"].strftime("%d %b %Y %H:%M:%S")

            elif test['status'] == "Specimen Received" or test['status'] == "Specimen Received" or test['status'] == "Being Analyzed":
                #test["collected_by"] =
                test["collected_at"] = test["date_ordered"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["receieved_at"] = test["collected_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["collected_at"] = test["collected_at"].strftime("%d %b %Y %H:%M:%S")
                test["receieved_at"] = test["receieved_at"].strftime("%d %b %Y %H:%M:%S")

            elif test['status'] == "Pending Verification":
                test["collected_at"] = test["date_ordered"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["receieved_at"] = test["collected_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test['completed_at'] = test["receieved_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["collected_at"] = test["collected_at"].strftime("%d %b %Y %H:%M:%S")
                test["receieved_at"] = test["receieved_at"].strftime("%d %b %Y %H:%M:%S")
                test['completed_at']  = test['completed_at'].strftime("%d %b %Y %H:%M:%S")
                test['measures'] = simulateMeasures(test_types[test_id]["measures"])

            elif test['status'] == "Analysis Complete" or test['status'] ==  "Reveiwed":
                test["collected_at"] = test["date_ordered"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["receieved_at"] = test["collected_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test['completed_at'] = test["receieved_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test['reviewed_at'] = test["completed_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["collected_at"] = test["collected_at"].strftime("%d %b %Y %H:%M:%S")
                test["receieved_at"] = test["receieved_at"].strftime("%d %b %Y %H:%M:%S")
                test['completed_at']  = test['completed_at'].strftime("%d %b %Y %H:%M:%S")
                test['reviewed_at']  = test['reviewed_at'].strftime("%d %b %Y %H:%M:%S")
                test['measures'] = simulateMeasures(test_types[test_id]["measures"])

            test['date_ordered'] = test['date_ordered'].strftime("%s")
            db.save(test)
'''

def simulateMeasures(measures):
    test_measures = {}

    for measure, params in measures.items():
        if params['type'] == 'Numeric':
            test_measures[measure] = str(random.random() * float(params['maximum']) * random.choice([1,1.5]))
        else:
            test_measures[measure] = random.choice(params['options'])
    return test_measures

def initializeViews():
    view = ViewDefinition('tests', 'testStatus', '''function(doc) {
        if (doc.type && doc.type == 'test'){
                emit(doc.status, doc);
            }
        }''')

    view.get_doc(db)
    # The view is not yet stored in the database, in fact, design doc doesn't
    # even exist yet. That can be fixed using the `sync` method:
    view.sync(db)

    view = ViewDefinition('tests', 'testByOrderer', '''function(doc) {
            if (doc.type && doc.type == 'test'){
                    emit(doc.ordered_by, doc);
                }
            }''')

    view.get_doc(db)
    # The view is not yet stored in the database, in fact, design doc doesn't
    # even exist yet. That can be fixed using the `sync` method:
    view.sync(db)

    view = ViewDefinition('users', 'teams', '''function(doc) {
            if (doc.type && doc.type == 'user' && doc.team){
                    emit(doc.team, doc._id);  
                }
            }''')

    view.get_doc(db)
    # The view is not yet stored in the database, in fact, design doc doesn't
    # even exist yet. That can be fixed using the `sync` method:
    view.sync(db)

if __name__ =='__main__':
    intializeFacts()
