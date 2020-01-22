#Written by Timothy Mtonga
#This is the main thread for the application

import os
import json
import csv
from couchdb import Server
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template,redirect,session,flash,request,url_for

app = Flask(__name__, template_folder="views", static_folder="assets")

#Main application configuration
global db
config_file = "config/application.config"
settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

#optional configuration when running on rpi
if settings["using_rpi"] == "True":
    from utils.led_control import ledControl
    #from utils.voltage_checker import CheckVoltage

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
        for provider in db.view("_design/users/_view/teams",key=session.get('user').get('team'), limit=100):
            my_team.append(provider.value)

        #Get all records for my team that require attention
        team_records = {
            "selector": {
                "type": "test",
                "ordered_by": {"$in": my_team},
                "status": {"$in": ["Ordered","Specimen Collected","Analysis Complete","Rejected"]}
            },"limit": 50
        }

        for item in db.find(team_records):
            my_team_recs.append({'status': item.get('status'),'date':float(item.get('date_ordered')),
                                 'test': db.find({"selector": {"type":"test_type","test_type_id": item.get('test_type')}, "fields": ["_id"]}),
                            'name': db.get(item.get('patient_id')).get('name').title(),
                            'ordered_by': db.get(item.get("ordered_by")).get('name').title(),
                            'ordered_on':datetime.fromtimestamp(float(item.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                            'patient_id': item.get('patient_id')})

    #query for records to display on the main page
    for item in db.find(main_index_records) :
        records.append({'status': item.get('status'),"date":float(item.get('date_ordered')),
                                'test': db.find({"selector": {"type":"test_type","test_type_id": item.get('test_type')}, "fields": ["_id"]}),
                                 'name': db.get(item.get('patient_id')).get('name').title(),
                                 'ordered_on':datetime.fromtimestamp(float(item.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                                 'patient_id': item.get('patient_id')})

    #sort by date descending
    records = sorted(records, key=lambda e: e["date"], reverse= True)
    my_team_recs = sorted(my_team_recs, key=lambda e: e["date"], reverse= True)
    return render_template('main/index.html', orders = records, team_records = my_team_recs)

#route to login page
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
    return render_template('user/login.html', error=error, requires_keyboard=True)

@app.route("/users")
def users():
    current_users = db.find({"selector": { "type": "user"}, "limit": 200})
    return render_template("user/index.html", requires_keyboard=True, users =current_users)

@app.route("/user/create", methods=["POST"])
def create_user():
    user = db.get(request.form['username'])
    if user == None:
        provider = {'type': "user","name" : request.form["name"] ,  "_id": request.form['username'],
                    'password_hash': generate_password_hash(request.form["password"]),
        "role": request.form['role'],   'designation': request.form['designation']}
        if request.form['role'] == "Doctor":
            provider["team"] = request.form["team"]
        else:
            provider["ward"] = request.form["wardAllocation"]

        db.save(provider)
    else:
      current_users = db.find({"selector": { "type": "user"}, "limit": 200})
      return render_template("user/index.html", requires_keyboard=True, users =current_users, error="Username already exists")
    return redirect(url_for("users",success =  "New user created"))

@app.route("/user/<user_id>/update_password", methods=["GET", "POST"])
def change_password(user_id=None):
    if request.method == "POST":
        user = db.get(user_id)
        if user == None:
            return redirect(url_for("index", error = "User not found"))
        else:
            user["password_hash"] =  generate_password_hash(request.form["password"])
            db.save(user)
            return redirect(url_for("index"))
    else:
        return render_template("user/update_password.html", requires_keyboard=True,username = user_id)

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
    pending_sample = []
    records = []
    if (request.args.get("sample_draw") != None) and (request.args.get("sample_draw") != None):
            draw_sample = True
    patient = db.get(patient_id)
    pt= { 'name': patient.get('name'), 'gender': 'male' if patient.get('gender') == 'M' else 'female',
          'dob': datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), 'id': patient_id}
    mango = {"selector": { "type": "test","patient_id": patient_id},
             "fields": ["_id","status","Priority","ordered_by","date_ordered","test_type","sample_type","measures","specimen_types","clinical_history"], "limit": 50}

    for test in  db.find(mango):
        test["date"] = float(test["date_ordered"])
        test["date_ordered"] =  datetime.fromtimestamp(float(test["date_ordered"])).strftime('%d %b %Y %H:%S')
        test["test_details"] = db.find({"selector": {"type":"test_type","test_type_id": test.get('test_type')}, "fields": ["_id","measures", "specimen_requirements"]})
        if test["status"] == "Ordered" :
            pending_sample .append({"test_id":test["_id"],
                                    "specimen_type": test["test_details"][0]["specimen_requirements"][test["sample_type"]]["type_of_specimen"],
                                    "test_type": test["test_details"][0]["_id"],
                                    "container": test["test_details"][0]["specimen_requirements"][test["sample_type"]]["container"],
                                   "volume":test["test_details"][0]["specimen_requirements"][test["sample_type"]]["volume"],
                                   "units":test["test_details"][0]["specimen_requirements"][test["sample_type"]]["units"]
                                    })
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
    records = sorted(records, key=lambda e: e["date"], reverse= True)
    return render_template('patient/show.html',pt_details = pt,tests=records, pending_orders=pending_sample, collect_samples=draw_sample, requires_keyboard=True)

@app.route("/patient/<patient_id>/draw", methods=['GET'])
def patient_draw_samples(patient_id=None):
    records = []
    pending_sample = []
    if (request.args.get("sample_draw") != None) and (request.args.get("sample_draw") != None):
            draw_sample = True
    patient = db.get(patient_id)
    pt= { 'name': patient.get('name'), 'gender': 'male' if patient.get('gender') == 'M' else 'female',
          'dob': datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), 'id': patient_id}
    mango = {"selector": { "type": "test","patient_id": patient_id},
             "fields": ["_id","status","Priority","ordered_by","date_ordered","test_type","sample_type","measures","specimen_types","clinical_history"], "limit": 90}

    for test in  db.find(mango):
        test["date"] = float(test["date_ordered"])
        test["date_ordered"] =  datetime.fromtimestamp(float(test["date_ordered"])).strftime('%d %b %Y %H:%S')
        test["test_details"] = db.find({"selector": {"type":"test_type","test_type_id": test.get('test_type')}, "fields": ["_id","measures", "specimen_requirements"]})
        if test["status"] == "Ordered" :
            pending_sample .append({"test_id":test["_id"],
                                    "specimen_type": test["test_details"][0]["specimen_requirements"][test["sample_type"]]["type_of_specimen"],
                                    "test_type": test["test_details"][0]["_id"],
                                    "container": test["test_details"][0]["specimen_requirements"][test["sample_type"]]["container"],
                                   "volume":test["test_details"][0]["specimen_requirements"][test["sample_type"]]["volume"],
                                   "units":test["test_details"][0]["specimen_requirements"][test["sample_type"]]["units"]
                                    })

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
    records = sorted(records, key=lambda e: e["date"], reverse= True)
    return render_template('patient/show.html',pt_details = pt,tests=records, pending_orders=pending_sample, collect_samples=True, requires_keyboard=True)

#create a new lab test order
@app.route("/test/create", methods=['POST'])
def create_lab_order():
    for test in request.form.getlist('test_type[]'):
        new_test = {
                'ordered_by': session["user"]['username'],
                'date_ordered': datetime.now().strftime('%s') ,
                'status': 'Ordered',
                'sample_type' : request.form['specimen_type'],
                'clinical_history': request.form['clinical_history'],
                'Priority':request.form['priority'],
                'ward': session["location"],
                'patient_id': request.form['patient_id']
            }
        if len(test.split("|")) > 1:
            new_test['type'] =  "test panel"
            new_test['tests'] = {}
            for type in test.split("|"):
                new_test['tests'][type] = {}
        else:
             new_test['type'] =  'test'
             new_test['test_type'] = test
        db.save(new_test)

    if request.form["sampleCollection"] == "Collect Now":
        return redirect(url_for('patient_draw_samples', patient_id=request.form['patient_id']))
    else:
        return redirect(url_for('patient', patient_id=request.form['patient_id']))

#update lab test orders to specimen collected
@app.route("/test/<test_id>/collect_specimen")
def collect_specimens(test_id):
    tests = db.find({"selector" : {"type": "test", "_id": {"$in": test_id.split("^")}}})
    test_ids = []
    test_names = []
    if tests == None or tests == []:
        return redirect( url_for("index", error = "Tests not found"))
    patient = db.get(tests[0]["patient_id"])
    dr = tests[0]["ordered_by"]
    wards = {"4A":"19","4B":"20","MSS":"44","MHDU":"56"}

    for test in tests:
        test["status"] = "Specimen Collected"
        test["collected_by"] = session["user"]['username']
        test_ids.append(test["test_type"])
        test_names.append(db.find({"selector": {"type":"test_type","test_type_id": test["test_type"]}, "fields": ["short_name"]})[0]["short_name"])
        db.save(test)

    test_string = [patient["name"].replace(" ", "^"), patient["_id"], patient["gender"][0],
                     datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                     wards[tests[0]["ward"]] ,dr,tests[0]["clinical_history"],tests[0]["sample_type"],
                     datetime.now().strftime("%s"), ("^").join(test_ids), tests[0]["Priority"][0] ]

    labelFile = open("/tmp/test_order.lbl", "w+")
    labelFile.write("N\nq406\nQ203,027\nZT\n")
    labelFile.write('A5,10,0,1,1,2,N,"%s"\n' % patient["name"])
    labelFile.write('A5,40,0,1,1,2,N,"%s (%s)"\n' % (datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), patient["gender"][0]) )
    labelFile.write('b5,70,P,386,80,"%s$"\n' % ("~").join(test_string))
    labelFile.write('A5,170,0,1,1,2,N,"%s"\n' % (",").join(test_names))
    labelFile.write('A260,170,0,1,1,2,N,"%s" \n' % datetime.now().strftime("%d-%b %H:%M"))
    labelFile.write("P1\n")
    labelFile.close()
    os.system('sudo sh ~/print.sh /tmp/test_order.lbl')

    return redirect(url_for('patient', patient_id=patient.get("_id")))

#proces barcode from the main index page
@app.route("/process_barcode", methods=["POST"])
def barcode():
    #write function to handle different types of barcodes that we expect
    barcode_segments = request.form['barcode'].split("~")
    if (len(barcode_segments) == 1 ):
        patient = db.get(barcode_segments[0].strip())
        if patient == None:
            error = "No patient with this record"
            return redirect(url_for("index", error = error))
        elif patient.get("type") != 'patient':
            error = "No patient with this record"
            return redirect( url_for("index", error = error))
        else:
            return redirect(url_for('patient', patient_id=barcode_segments[0].strip()))
    elif (len(barcode_segments) == 5 ):
        #This section is for the npid qr code
        id = barcode_segments[1].strip()
        patient = db.get(id)

        if patient == None or patient.get("type") != 'patient':
            dob_format = "%d/%b/%Y"

            if "??" == barcode_segments[2].split("/")[0] and "???" == barcode_segments[2].split("/")[1]:
                dob_format = "??/???/%Y"
            elif "??" == barcode_segments[2].split("/")[0] and "???" != barcode_segments[2].split("/")[1]:
                dob_format = "??/%b/%Y"
            elif "??" != barcode_segments[2].split("/")[0] and "???" == barcode_segments[2].split("/")[1]:
                dob_format = "%d/???/%Y"

            doc = {'_id': id, 'name': barcode_segments[0], 'type': 'patient',
                   'dob':  datetime.strptime(barcode_segments[2], dob_format).strftime("%d-%m-%Y"),
                   'gender': barcode_segments[3]}
            db.save(doc)
        return redirect(url_for('patient', patient_id=id))
    else:
        error = "Wrong format for patient identifier. Please use the National patient Identifier"
        return redirect( url_for("index", error = error))

def collapse_test_orders(orders):
    if (("Full Blood Count" in orders) and ("Malaria Screening" in orders)):
        pass
        #pop those two out and combine them in one

    pass

#Application callbacks
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
    initialize_connection()
    if settings["using_rpi"] == "True":
        if request.path == "/":
            ledControl().turn_led_on()
        else:
            ledControl().turn_led_off()

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
    return {'now': datetime.now().strftime("%H:%M%p")}

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
def inject_power():
    if settings["using_rpi"] == "True":
        voltage = 100 #CheckVoltage().getVoltage()
        if voltage > 70:
            rating = "high"
        elif voltage > 30 and voltage < 70:
            rating = "medium"
        else:
            rating = "low"
    else:
        voltage=  100
        rating =  "high"

    return {"current_power": voltage, "power_class": rating}

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
    test_options = sorted(test_options.items(), key=lambda e: e[1]["name"])
    return {"test_options":  test_options}

@app.context_processor
def inject_panels():
    panels = []
    with open('test_panels.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                line_count += 1
                panels.append({"panel": row[1], "tests": row[3], "specimen_type": row[4].replace("|", ",")})

    panels = sorted(panels, key=lambda e: e["panel"])
    return {"panels":  panels}

@app.context_processor
def inject_containers():
    return {"containers": {'Sterile container': "blue_top_urine.png",
                           'Red top': "red_top.jpg", 'Baktech':"bactec.png",
                           'Conical container': "conical_contatiner.jpeg",
            'EDTA': 'purple_top.jpg', 'yellow top': "yellow_top.jpg"}}

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
