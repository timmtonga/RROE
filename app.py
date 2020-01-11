#Written by Timothy Mtonga
#This is the main thread for the application

import os
import json
from couchdb import Server
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template,redirect,session,flash,request,url_for
app = Flask(__name__, template_folder="views", static_folder="assets")

global db
config_file = "config/application.config"
settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

#Root page of application
@app.route("/")
def index():
    records = []
    my_team_recs = []
    #Based on role, pull the required information from the database
    if session["user"]["role"] == "Nurse":
        main_index_records = {
            "selector": {
                "type": "test",
                "ward": session.get('location'),
                "status": {"$in": ["Ordered","Specimen Collected","Analysis Complete", "Rejected"]}
            }
        }

    else:
        main_index_records = {
            "selector": {
                "type": "test",
                "ordered_by": session["user"]['username'],
                "status": {"$in": ["Ordered","Specimen Collected","Analysis Complete","Rejected"]}
            }
        }

        #Get my team members and then all tests requested by members of my team
        my_team = []
        for provider in db.view("_design/users/_view/teams",key=session.get('user').get('team'), limit=1000):
            my_team.append(provider.value)

        #Get all records for my team that require attention
        team_records = {
            "selector": {
                "type": "test",
                "ordered_by": {"$in": my_team},
                "status": {"$in": ["Ordered","Specimen Collected","Analysis Complete","Rejected"]}
            },"limit": 90
        }

        for item in db.find(team_records):
            my_team_recs.append({'status': item.get('status'),
                                 'test': db.find({"selector": {"type":"test_type","test_type_id": item.get('test_type')}, "fields": ["_id"]}),
                            'name': db.get(item.get('patient_id')).get('name').title(),
                            'ordered_by': db.get(item.get("ordered_by")).get('name').title(),
                            'ordered_on':datetime.fromtimestamp(float(item.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                            'patient_id': item.get('patient_id')})


    for item in db.find(main_index_records) :
        records.append({'status': item.get('status'),
                                'test': db.find({"selector": {"type":"test_type","test_type_id": item.get('test_type')}, "fields": ["_id"]}),
                                 'name': db.get(item.get('patient_id')).get('name').title(),
                                 'ordered_on':datetime.fromtimestamp(float(item.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                                 'patient_id': item.get('patient_id')})

    return render_template('main/index.html', orders = records, team_records = my_team_recs)

@app.route("/login", methods=["GET", "POST"])
def login():
    error= None
    if request.method == "POST":
        user = db.get(request.form['username'])
        if user == None:
            error = "Invalid username. Please try again."
        else:
            if not check_password_hash(user['password_hash'], request.form['password']):
                error = "Wrong password. Please try again."
            else:
                session["logged_in"] = True
                session["user"] = {'username': request.form['username'],
                                   'role': user['role'],
                                   'current_user': user.get('name','Unknown'),
                                   'team': user.get('team', 'Unassigned'),
                                   'rank': user.get('designation', 'Unassigned')}
                return redirect(url_for('select_location'))

    session["user"] = None
    session["logged_in"] = None
    return render_template('user/login.html', error=error)

@app.route("/user/new")
def new_user():
    return "New User Page"

@app.route("/user/create", methods=["Post"])
def create_user():
    #password_hash = generate_password_hash("request.form['password']")
    return "New user created"

@app.route("/select_location", methods=["GET", "POST"])
def select_location():
    error= None
    if request.method == "POST":
        if request.form['location'] == '' :
            error = "Invalid location. Please try again."
        else:
            session["location"] = request.form['location']
            return redirect(url_for('index'))

    session["location"] = None
    return render_template('user/select_location.html', error=error, options=locations_options())

@app.route("/patient/<patient_id>", methods=['GET'])
def patient(patient_id=None):
    draw_sample = False
    records = []
    if (request.args.get("sample_draw") != None) and (request.args.get("sample_draw") != None):
            draw_sample = True
    patient = db.get(patient_id)
    pt= { 'name': patient.get('name'), 'gender': 'male' if patient.get('gender') == 'M' else 'female',
          'dob': datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), 'id': patient_id}
    mango = {"selector": { "type": "test","patient_id": patient_id},
             "fields": ["_id","status","Priority","ordered_by","date_ordered","test_type","sample_type","measures"], "limit": 90}

    for test in  db.find(mango):
        test["date_ordered"] =  datetime.fromtimestamp(float(test["date_ordered"])).strftime('%d %b %Y %H:%S')
        test["test_details"] = db.find({"selector": {"type":"test_type","test_type_id": test.get('test_type')}, "fields": ["_id","measures"]})

        try:
            for measure in test.get("measures"):
                test["numeric_measures"] = []
                test["critical"] = {}
                if test['test_details'][0]["measures"][measure].get("minimum") != None :
                    test["numeric_measures"].append(measure)
                    if float(test["measures"][measure]) < float(test['test_details'][0]["measures"][measure].get("minimum")):
                        test["critical"][measure] = "low"
                    elif float(test["measures"][measure]) > float(test['test_details'][0]["measures"][measure].get("maximum")):
                        test["critical"][measure] = "high"
        except:
            pass
        records.append(test)

    return render_template('patient/show.html',pt_details = pt,tests=records, pending_orders=False, collect_samples=draw_sample)

@app.route("/patient/<patient_id>/draw", methods=['GET'])
def patient_draw_samples(patient_id=None):
    patient = db.get(patient_id)
    pt= { 'name': patient.get('name'), 'gender': 'male' if patient.get('gender') == 'M' else 'female',
          'dob': datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), 'id': patient_id}
    mango = {"selector": { "type": "test","patient_id": patient_id}}
    records =  db.find(mango)

    return render_template('patient/show.html',pt_details = pt,tests=records, pending_orders=True, collect_samples=True)

#create a new lab test order
@app.route("/test/create", methods=['POST'])
def create_lab_order():
    for test in request.form.getlist('test_type[]'):
        test = {
                'ordered_by': session["user"]['username'],
                'date_ordered': datetime.now().strftime('%s') ,
                'status': 'Ordered',
                'test_type': test,
                'sample_type' : request.form['specimen_type'],
                'clinical_history': request.form['clinical_history'],
                'type': 'test',
                'Priority':request.form['priority'],
                'ward': session["location"],
                'patient_id': request.form['patient_id']
            }
    db.save(test)

    if request.form["sampleCollection"] == "Collect Now":
        return redirect(url_for('patient_draw_samples', patient_id=request.form['patient_id']))
    else:
        return redirect(url_for('patient', patient_id=request.form['patient_id']))

#update lab test orders to specimen collected
@app.route("/test/<test_id>/collect_specimen")
def collect_specimens(test_id=[]):
    pat_id = 'DFOGLS'
    try:
        labelFile = open("/tmp/test_order.lbl", "w+")
        labelFile.write("N\nq406\nQ203,027\nZT\n")
        labelFile.write('A25,10,0,1,1,2,N,"James Phiri"\n')
        labelFile.write('A25,40,0,1,1,2,N,"2 Jul, 2019"\n')
        labelFile.write('b20,70,P,386,80,"James Phiri~XYXKRQ~M~19850115~4B~Dr Wangui~Septic Sores~201907111235~FBC^MPS^ESR~S"\n')
        labelFile.write('A25,120,0,1,1,2,N,"FBC, MPS & ESR"\n')
        labelFile.write('A25,150,0,1,1,2,N,%s \n' % datetime.utcnow().strftime("%d-%b-%y %H:%M"))
        labelFile.write("P1\n")
        labelFile.close()
        os.system('sh ~/print.sh /tmp/test_order.lbl')
    except:
        pass
    return redirect(url_for('patient', patient_id=pat_id))

#proces barcode from the main index page
@app.route("/process_barcode", methods=["POST"])
def barcode():
    #write function to handle different types of barcodes that we expect
    barcode_segments = request.form['barcode'].split("~")
    if (len(barcode_segments) == 1 ):
        patient = db.get(barcode_segments[0].strip())
        if patient == None:
            error = "No patient with this record"
            return redirect("home", error = error)
        elif patient.get("type") != 'patient':
            error = "No patient with this record"
            return redirect("home", error = error)
        else:
            return redirect(url_for('patient', patient_id=barcode_segments[0].strip()))
    elif (len(barcode_segments) == 5 ):
        #This section is for the npid qr code
        id = barcode_segments[1].strip()
        patient = db.get(id)
        if patient == None or patient.get("type") != 'patient':
            doc = {'_id': id, 'name': barcode_segments[0], 'type': 'patient',
                   'dob':  datetime.strptime(barcode_segments[2], "%d/%b/%Y").strftime("%d-%m-%Y"),
                   'gender': barcode_segments[3]}
            db.save(doc)
        return redirect(url_for('patient', patient_id=id))
    else:
        error = "Wrong format for patient identifier. Please use the National patient Identifier"
        return redirect("home", error = error)

def collapse_test_orders(orders = []):
    if (("Full Blood Count" in orders) and ("Malaria Screening" in orders)):
        pass
        #pop those two out and combine them in one

    pass

#Application callbacks
@app.before_request
def initialize_connection():
    #Connect to a couchdb instance
    couchConnection = Server("http://%s:%s@%s:%s/" %
                             (settings["couch"]["user"],settings["couch"]["passwd"],
                              settings["couch"]["host"],settings["couch"]["port"]))
    global db
    # Connect to a database or Create a Database
    try:
        db = couchConnection[settings["couch"]["database"]]
    except:
        db = couchConnection.create(settings["couch"]["database"])

@app.before_request
def check_authentication():

    if request.path != "/login":
        try:
            session["logged_in"]
            if request.path != "/select_location":
                try:
                    session["location"]
                except:
                    return  redirect(url_for('select_location'))
        except:
            return redirect(url_for('login'))

#Context processors. Used to get data in views
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow().strftime("%d-%b-%y %H:%M")}

def locations_options():
    return [["MSS", "Medical Short Stay"], ["4A", "Medical Female Ward"], ["4B", "Medical Male Ward"], ["MHDU", "Medical HDU"]]

@app.context_processor
def inject_user():
    return {'current_user': session.get("user")}

@app.context_processor
def inject_facility():
    return {'current_facility': settings["facility"]}

@app.context_processor
def inject_specimen_types():
    specimen_types = []
    test_file = "test_details.json"
    tests = {}
    with open(test_file) as json_file:
        tests = json.load(json_file)
    for key, value in tests.items():
        specimen_types.append([key,value['specimen_type_id']])
    specimen_types.sort()
    return {'specimen_types': [specimen_types[i * 2:(i + 1) * 2] for i in range((len(specimen_types) + 2 - 1) // 2 )] }

@app.context_processor
def inject_tests():
    test_options = {}
    test_file = "test_details.json"
    with open(test_file) as json_file:
        specimen_types = json.load(json_file)

    for specimen_type, tests in specimen_types.items():
        for test_name, test in tests['tests'].items():
            if (test_options.get(test.get("test_type_id")) == None ):
                test_options[test.get("test_type_id")] = {"name": test_name, "specimen_types" :[tests['specimen_type_id']] }
            elif tests['specimen_type_id'] not in test_options[test.get("test_type_id")]["specimen_types"]:
                test_options[test.get("test_type_id")]["specimen_types"].append(tests['specimen_type_id'])

    return {"test_options":  test_options}

#Error handling pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('main/404.html'), 404

@app.errorhandler(422)
def not_found_error(error):
    return render_template('main/422.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('main/500.html'), 500

if __name__ =='__main__':
    app.secret_key = os.urandom(25)
    app.run(port="7500", debug=True, host='0.0.0.0')
