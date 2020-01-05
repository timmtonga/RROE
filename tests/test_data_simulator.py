from couchdb import Server # importing couchdb
from couchdb.design import ViewDefinition
import random
import datetime
from werkzeug.security import generate_password_hash

couch = Server('http://admin:rootpwd@127.0.0.1:5984/')
del couch['rroe_trial']

# Creating Database
try:
    db = couch['rroe_trial']
except:
    db = couch.create('rroe_trial')

orderers = []
test_status = ["Ordered", "Specimen Collected", "Specimen Received", "Being Analyzed",
               "Pending Verification", "Analysis Complete", "Reveiwed"]

designations = {'N' : 'Nurse', 'S': 'Siter-in-charge' , 'M': 'Matron',
                'I': 'Intern Medical Offcer','R': 'Registrar', 'C': 'Consultant'}

test_types = {'GeneXpert':{'short_name':'GXp', 'measures':{'MTB':{'type':'Categorical', 'options':['Positive', 'Negative']}}},
              'Gram Stain':{'short_name':'GS', 'measures':{'Gram':{'type':'Categorical', 'options':['No organism seen', 'Gram positive cocci (clusters)', 'Gram positive cocci (chains)',
                                                                                                    'Gram positive diplococci', 'Gram positive bacilli', 'Gram positive cocco-bacilli', 'Gram negative cocci',
                                                                                                    'Gram negative bacilli', 'Gram negative cocco-bacilli', 'Gram negative diplococci', 'Gram variable cocci',
                                                                                                    'Gram variable  bacilli', 'Gram variable cocco-bacilli', 'Yeast cells seen']}}},
              'Culture & Sensitivity':{'short_name':'C&S', 'measures':{'Culture':{'type':'Categorical', 'options':['Growth', 'No growth', 'Mixed growth; no predominant organism',
                                                                                                                   'Growth of normal flora; no pathogens isolated', 'Growth of contaminants']}}},
              'Cell Count':{'short_name':'ClCt', 'measures':{'WBC':{'type':'Numeric', 'minimum':'0.000', 'maximum':'1000000.000'},
                                                             'RBC':{'type':'Numeric', 'minimum':'0.000', 'maximum':'1000000.000'}}},
              'India Ink':{'short_name':'II', 'measures':{'India ink':{'type':'Categorical', 'options':['Positive', 'Negative']}}},
              'ZN Stain':{'short_name':'ZN', 'measures':{'ZN':{'type':'Categorical', 'options':['Scanty AAFB seen', '1+ AAFB seen', '2+ AAFB seen', '3+ AAFB seen', 'No AAFB seen']}}},
              'Wet prep':{'short_name':'WP', 'measures':{'wet prep':{'type':'Categorical', 'options':['Trichomonas vaginalis seen', 'Yeast cells seen', 'Spermatozoa seen']}}},
               'Stool Analysis':{'short_name':'StoA', 'measures':{'Consistency':{'type':'Categorical',
                                                                                 'options':['Formed', 'Semi-formed', 'Unformed', 'Watery', 'Rice appearance']}}},
              'Malaria Screening':{'short_name':'MalScr', 'measures':{'Blood film':{'type':'Categorical', 'options':['No parasite seen',
                                                                                                                     '+ (1-10 parasites/100 fields)', '++ (11-99 parasites/100 field)', '+++ (1-10 parasites /field)',
                                                                                                                     '++++ (>10 parasites/field)']},
                                                                      'Malaria Species':{'type':'Categorical', 'options':['Plasmodium falciparum', 'Plasmodium ovale',
                                                                                                                          'Plasmodium vivax', 'Plasmodium malariae', 'Plasmodium knowlesi']},
                                                                      'MRDT':{'type':'Categorical', 'options':['Positive', 'Negative', 'Invalid']}}},
              'Syphilis Test':{'short_name':'STS', 'measures':{'RPR':{'type':'Categorical', 'options':['Reactive', 'Non-reactive']},
                                                               'VDRL':{'type':'Categorical', 'options':['Reactive', 'Non-reactive']},
                                                               'TPHA':{'type':'Categorical', 'options':['Reactive', 'Non-reactive']}}},
              'Hepatitis B Test':{'short_name':'HBsAg', 'measures':{'Hepatitis B':{'type':'Categorical', 'options':['Positive', 'Negative', 'Invalid']}}},
              'Hepatitis C Test':{'short_name':'HCVAB', 'measures':{'Hepatitis C':{'type':'Categorical', 'options':['Positive', 'Negative', 'Invalid']}}},
              'Rheumatoid Factor Test':{'short_name':'RF', 'measures':{'Rheumatoid Factor':{'type':'Categorical', 'options':['Positive', 'Negative']}}},
              'ABO Blood Grouping':{'short_name':'ABO', 'measures':{'Grouping':{'type':'Categorical', 'options':['A RhD Positive', 'B RhD Positive', ''
                                                                                                                                                     'AB RhD Positive', 'O RhD Positive', 'A RhD Negative', 'B RhD Negative',
                                                                                                                 'AB RhD Negative', 'O RhD Negative']}}},
              'Liver Function Tests':{'short_name':'LFT', 'measures':{'ALT/GPT':{'type':'Numeric', 'minimum':'0.000', 'maximum':'32.000'},
                                                                      'AST/GOT':{'type':'Numeric', 'minimum':'0.000', 'maximum':'37.000'},
                                                                      'GGT/r-GT':{'type':'Numeric', 'minimum':'0.000', 'maximum':'32.000'},
                                                                      'Bilirubin Direct(BID)':{'type':'Numeric', 'minimum':'0.000', 'maximum':'0.200'},
                                                                      'Bilirubin Total(BIT))':{'type':'Numeric', 'minimum':'0.300', 'maximum':'1.200'},
                                                                      'Albumin(ALB)':{'type':'Numeric', 'minimum':'3.200', 'maximum':'5.000'},
                                                                      'Total Protein(PRO)':{'type':'Numeric', 'minimum':'6.000', 'maximum':'8.300'},
                                                                      'ALPU':{'type':'Numeric', 'minimum':'64.000', 'maximum':'306.000'}}},
              'Renal Function Test':{'short_name':'RFT', 'measures':{'Urea':{'type':'Numeric', 'minimum':'18.000', 'maximum':'55.000'},
                                                                     'Creatinine':{'type':'Numeric', 'minimum':'0.600', 'maximum':'1.100'}}},
              'Lipogram':{'short_name':'LIPO', 'measures':{'Triglycerides(TG)':{'type':'Numeric', 'minimum':'35.000', 'maximum':'135.000'},
                                                           'Cholestero l(CHOL)':{'type':'Numeric', 'minimum':'110.000', 'maximum':'230.000'},
                                                           'HDL Direct (HDL-C)':{'type':'Numeric', 'minimum':'42.000', 'maximum':'88.000'},
                                                           'LDL Direct (LDL-C)':{'type':'Numeric', 'minimum':'0.000', 'maximum':'130.000'}}},
              'FBC':{'short_name':'FBC', 'measures':{'RBC':{'type':'Numeric', 'minimum':'3.500', 'maximum':'5.500'},
                                                     'HGB':{'type':'Numeric', 'minimum':'11.000', 'maximum':'16.000'}, 'HCT':{'type':'Numeric', 'minimum':'37.000', 'maximum':'54.000'},
                                                     'MCV':{'type':'Numeric', 'minimum':'80.000', 'maximum':'100.000'},
                                                     'MCH':{'type':'Numeric', 'minimum':'23.000', 'maximum':'34.000'},
                                                     'MCHC':{'type':'Numeric', 'minimum':'33.000', 'maximum':'36.000'},
                                                     'PLT':{'type':'Numeric', 'minimum':'122.000', 'maximum':'330.000'},
                                                     'RDW-SD':{'type':'Numeric', 'minimum':'37.000', 'maximum':'54.000'},
                                                     'RDW-CV':{'type':'Numeric', 'minimum':'10.000', 'maximum':'16.000'},
                                                     'PDW':{'type':'Numeric', 'minimum':'9.000', 'maximum':'17.000'}, 'MPV':{'type':'Numeric', 'minimum':'6.000', 'maximum':'10.000'},
                                                     'PCT':{'type':'Numeric', 'minimum':'0.170', 'maximum':'0.350'}, 'NEUT%':{'type':'Numeric', 'minimum':'27.000', 'maximum':'60.000'},
                                                     'LYMPH%':{'type':'Numeric', 'minimum':'20.000', 'maximum':'40.000'},
                                                     'MONO%':{'type':'Numeric', 'minimum':'2.000', 'maximum':'10.000'},
                                                     'EO%':{'type':'Numeric', 'minimum':'0.000', 'maximum':'12.000'}, 'BASO%':{'type':'Numeric', 'minimum':'0.000', 'maximum':'1.000'},
                                                     'NEUT#':{'type':'Numeric', 'minimum':'0.820', 'maximum':'4.100'},
                                                     'LYMPH#':{'type':'Numeric', 'minimum':'1.260', 'maximum':'3.620'},
                                                     'MONO#':{'type':'Numeric', 'minimum':'0.120', 'maximum':'0.560'},
                                                     'EO#':{'type':'Numeric', 'minimum':'0.000', 'maximum':'0.780'}, 'BASO#':{'type':'Numeric', 'minimum':'0.000', 'maximum':'0.070'},
                                                     'WBC':{'type':'Numeric', 'minimum':'4.000', 'maximum':'10.000'}, 'P-LCC':{'type':'Numeric', 'minimum':'30.000', 'maximum':'90.000'},
                                                     'P-LCR':{'type':'Numeric', 'minimum':'11.000', 'maximum':'45.000'}}},
              'Electrolytes':{'short_name':'E', 'measures':{'K':{'type':'Numeric', 'minimum':'3.500', 'maximum':'5.500'},
                                                            'Na':{'type':'Numeric', 'minimum':'135.000', 'maximum':'145.000'},
                                                            'Cl':{'type':'Numeric', 'minimum':'98.000', 'maximum':'108.000'}}}
              }

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
    initializeViews()

def simulateProviders():
    dr =  1
    nu = 1
    for i in range(1,20):
        role = random.choice('NNND')
        provider = {
                'type': 'user',
                'name' : names[random.randint(0, (len(names)-1))] + ' ' + surnames[random.randint(0, (len(surnames)-1))],
                'dob': datetime.datetime.strptime('{} {}'.format(random.randint(1, 366), random.randint(1930,2019)), '%j %Y').strftime("%d-%m-%Y"),
                'gender': random.choice('FM'), 'password_hash': generate_password_hash('letmein')
        }

        if (role == 'N'):
            print("nurse" + str(i))
            provider["_id"] = "nurse" + str(i)
            provider['role']  = 'Nurse'
            provider['designation'] =  designations[random.choice('NNNNNSSM')]
            nu +=1
        else:
            print("doctor" + str(i))
            provider["_id"] = "doctor" + str(i)
            provider['role']  = 'Doctor'
            provider['designation'] = designations[random.choice('IIIIRRRC')]
            provider['team'] = random.choice("ABCD")
            dr += 1

        db.save(provider)
        if role == 'D':
            orderers.append(provider['_id'])

def simulatePatients():
    for i in range(1,100):
        id = ''.join(random.choice('34679ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(6))
        dob = datetime.datetime.strptime('{} {}'.format(random.randint(1, 366), random.randint(1930,2019)), '%j %Y').strftime("%d-%m-%Y")
        # Creating document
        doc = {'_id': id, 'name': names[random.randint(0, (len(names)-1))] + ' ' + surnames[random.randint(0, (len(surnames)-1))],
                    'dob': dob, 'gender': random.choice('FM'), 'type': 'patient',}

        db.save(doc)

        nTests = random.randint(0,10)

        for n in range(0,nTests) :
            pass
            test = {
                'ordered_by': random.choice(orderers),
                'date_ordered': (datetime.datetime.now() - datetime.timedelta(days= random.randint(0,5))),
                'status': test_status[random.randint(0, (len(test_status)-1))],
                'test_type': random.choice(test_types.keys()),
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
                test['measures'] = simulateMeasures(test['test_type'])

            elif test['status'] == "Analysis Complete" or test['status'] ==  "Reveiwed":
                test["collected_at"] = test["date_ordered"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["receieved_at"] = test["collected_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test['completed_at'] = test["receieved_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test['reviewed_at'] = test["completed_at"] + datetime.timedelta(minutes=random.randint(1,1000))
                test["collected_at"] = test["collected_at"].strftime("%d %b %Y %H:%M:%S")
                test["receieved_at"] = test["receieved_at"].strftime("%d %b %Y %H:%M:%S")
                test['completed_at']  = test['completed_at'].strftime("%d %b %Y %H:%M:%S")
                test['reviewed_at']  = test['reviewed_at'].strftime("%d %b %Y %H:%M:%S")
                test['measures'] = simulateMeasures(test['test_type'])

            test['date_ordered'] = test['date_ordered'].strftime("%s")
            db.save(test)

def simulateMeasures(testType):
    test_measures = {}
    measures = test_types[testType]['measures']

    for measure, params in measures.items():
        if test_types[testType]['measures'][measure]['type'] == 'Numeric':
            test_measures[measure] = random.random() * float(test_types[testType]['measures'][measure]['maximum']) * random.choice([1,1.5])
        else:
            test_measures[measure] = random.choice(test_types[testType]['measures'][measure]['options'])

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
