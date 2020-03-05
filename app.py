#Written by Timothy Mtonga
#This is the main thread for the application
#!/usr/bin/python

import os
import re
import json
import random
from utils import misc
from couchdb import Server
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template,redirect,session,flash,request,url_for

app = Flask(__name__, template_folder="views", static_folder="assets")
app.secret_key = os.urandom(25)

#Main application configuration
global db
settings = misc.initialize_settings()

#optional configuration when running on rpi
if settings["using_rpi"] == "True":
    from utils.led_control import ledControl
    from utils.voltage_checker import CheckVoltage

#Root page of application
@app.route("/")
def index():
    records = []
    my_team_recs = []
    test_names = {}
    tests = db.find({ "selector": {"type": "test_type"},"fields": ["_id","test_type_id"],"limit":5000})
    for test in tests:
        test_names[test["test_type_id"]] =  test["_id"]
    #Based on role, pull the required information from the database
    if session["user"]["role"] in ['Nurse', 'Student'] :
        main_index_records = {
            "selector": {
                "type": {"$in": ["test","test panel"]},
                "ward": session.get('location'),
                "status": {"$in": ["Ordered","Specimen Collected","Analysis Complete", "Rejected"]}
            },"limit":100
        }

    else:
        main_index_records = {
            "selector": {
                "type": {"$in": ["test","test panel"]},
                "ordered_by": session["user"]['username'],
                "status": {"$in": ["Ordered","Specimen Collected","Analysis Complete","Rejected"]}
            },"limit":100
        }

        #Get my team members and then all tests requested by members of my team
        my_team = []
        for provider in db.view("_design/users/_view/teams",key=session.get('user').get('team'), limit=100):
            my_team.append(provider.value)

        #Get all records for my team that require attention
        team_records = {
            "selector": {
                "type": {"$in": ["test","test panel"]},
                "ordered_by": {"$in": my_team},
                "status": {"$in": ["Ordered","Specimen Collected","Analysis Complete","Rejected"]}
            },"limit": 100
        }

        for item in db.find(team_records):
            team_test_detail = {'status': item.get('status'),'date':float(item.get('date_ordered')),"id": item["_id"],
                            'name': db.get(item.get('patient_id')).get('name').title(),
                            'ordered_by': db.get(item.get("ordered_by")).get('name').title(),
                            'ordered_on':datetime.fromtimestamp(float(item.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                            "id": item["_id"],'patient_id': item.get('patient_id')}

            if item.get("type") == "test":
               team_test_detail['test'] = test_names[item.get('test_type')]
            else:
                team_test_detail['test'] = item.get('panel_type')
            my_team_recs.append(team_test_detail)
    #query for records to display on the main page
    for item in db.find(main_index_records) :
        test_detail = {'status': item.get('status'),"date":float(item.get('date_ordered')),
                                 'name': db.get(item.get('patient_id')).get('name').title(),
                                 'ordered_on':datetime.fromtimestamp(float(item.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                                 "id": item["_id"],'patient_id': item.get('patient_id')}

        if item.get("type") == "test":
            test_detail['test'] = test_names[item.get('test_type')]
        else:
            test_detail['test'] = item.get('panel_type')
        records.append(test_detail)

    #sort by date descending
    records = sorted(records, key=lambda e: e["date"], reverse= True)
    my_team_recs = sorted(my_team_recs, key=lambda e: e["date"], reverse= True)
    return render_template('main/index.html', orders = records, team_records = my_team_recs, current_facility = misc.current_facility())

#proces barcode from the main index page
@app.route("/process_barcode", methods=["POST"])
def barcode():
    #write function to handle different types of barcodes that we expect
    barcode_segments = request.form['barcode'].split("~")
    if (len(barcode_segments) == 1 ):
        patient = db.get(barcode_segments[0].strip())
        if patient == None:
            flash("No patient with this record", 'error')
            return redirect(url_for("index"))
        elif patient.get("type") != 'patient':
            flash("No patient with this record", "error")
            return redirect( url_for("index"))
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

            doc = {'_id': id, 'name': barcode_segments[0].replace(id,""), 'type': 'patient',
                   'dob':  datetime.strptime(barcode_segments[2], dob_format).strftime("%d-%m-%Y"),
                   'gender': barcode_segments[3]}
            db.save(doc)
        return redirect(url_for('patient', patient_id=id))
    else:
        flash("Wrong format for patient identifier. Please use the National patient Identifier", "error")
        return redirect( url_for("index"))

###### PATIENT ROUTES ###########
@app.route("/patient/<patient_id>", methods=['GET'])
def patient(patient_id):
    draw_sample = False
    pending_sample = []
    records = []
    details_of_test = {}
    if (request.args.get("sample_draw") == "True"):
            draw_sample = True

    #get patient details and arrange them in a way that is needed
    patient = db.get(patient_id)
    pt= { 'name': patient.get('name'), 'gender': 'male' if patient.get('gender') == 'M' else 'female',
          "age": misc.calculate_age(datetime.strptime(patient.get('dob'), "%d-%m-%Y").date()),
          'dob': datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), 'id': patient_id}

    #get tests for pateint
    mango = {"selector": {"type": {"$in": ["test","test panel"]},"patient_id": patient_id},
             "fields": ["_id","type","status","Priority","ordered_by","date_ordered","rejection_reason","collection_id",
                        "test_type","sample_type","measures","specimen_types","clinical_history","panel_type","tests"], "limit": 500}

    for test in  db.find(mango):
        test_record = {"date_ordered":  datetime.fromtimestamp(float(test["date_ordered"])).strftime('%d %b %Y %H:%S'), "id": test.get("_id")}
        test_record["type"] = test.get("type")
        test_record["status"] = test.get("status")
        test_record["priority"] = test.get("Priority")
        test_record["date"]= float(test["date_ordered"])
        test_record["collection_id"] = test.get("collection_id", "")
        test_record["history"] = test.get("clinical_history")
        test_record["ordered_by"] = test.get("ordered_by")
        test_record["rejection_reason"] = test.get("rejection_reason")
        test_record["test_type"] = "test" if test.get("type") == "test" else "test panel"

        if test.get("type") == "test":
            if details_of_test.get(test.get('test_type')) == None:
                details_of_test[test.get('test_type')] = db.find({"selector": {"type":"test_type","test_type_id": test.get('test_type')}, "fields": ["_id","measures", "specimen_requirements", "department"]})[0]

            test_record["test_name"] = details_of_test[test.get('test_type')]["_id"]
            if test["status"] == "Ordered":
                pending_sample .append({"test_id":test["_id"],
                                    "specimen_type": details_of_test[test.get('test_type')]["specimen_requirements"][test["sample_type"]]["type_of_specimen"],
                                    "test_type": details_of_test[test.get('test_type')]["_id"],"department": details_of_test[test.get('test_type')]["department"],
                                    "container": details_of_test[test.get('test_type')]["specimen_requirements"][test["sample_type"]]["container"],
                                   "volume":details_of_test[test.get('test_type')]["specimen_requirements"][test["sample_type"]]["volume"],
                                   "units":details_of_test[test.get('test_type')]["specimen_requirements"][test["sample_type"]]["units"],
                                    "test_name": details_of_test[test.get('test_type')]["_id"]
                                    })
            test_record['measures'] = get_test_measures(test,details_of_test[test.get('test_type')])
        elif  test.get("type") == "test panel":
            test_record["test_name"] = test["panel_type"]
            test_record["panel_test_details"] = {}
            for panel_test in test.get("tests").keys():
                if details_of_test.get(panel_test) == None:
                    details_of_test[panel_test] = db.find({"selector": {"type":"test_type","test_type_id": panel_test}, "fields": ["_id","measures", "specimen_requirements", "department"]})[0]
                test_record["panel_test_details"][panel_test] = {"test_name": details_of_test[panel_test]["_id"]}
                test_record["panel_test_details"][panel_test]['measures'] = get_test_measures(test.get("tests")[panel_test],details_of_test[panel_test])
            if test["status"] == "Ordered":
                panel_details = {"test_id":test["_id"],"specimen_type": specimen_type_map(test['sample_type']),
                                                "test_name": test["panel_type"]
                                                }
                if panel_details["specimen_type"] == "Urine":
                    panel_details["container"] = 'Conical container'
                    panel_details["volume"] = "15 "
                    panel_details["units"] = "ml"
                elif panel_details["specimen_type"] == "Blood" and panel_details["test_name"] == "MC&S":
                    panel_details["container"] = 'Baktech'
                    panel_details["volume"] = "5 "
                    panel_details["units"] = "ml"
                else:
                    panel_details["container"] = 'Red top'
                    panel_details["volume"] = "4"
                    panel_details["units"] = "ml"
                pending_sample .append(panel_details)

        if test != None:
            records.append(test_record)

    records = sorted(records, key=lambda e: e["date"], reverse= True)
    permitted_length = 86 - 50 - len(patient.get('name')) - len(patient.get('_id'))
    return render_template('patient/show.html',pt_details = pt,tests=records, pending_orders= pending_sample, containers =  misc.container_options(),
                           collect_samples=draw_sample, doctors = prescribers(),ch_length= permitted_length,requires_keyboard=True,
                           test_options= inject_tests(), specimen_types=inject_specimen_types(),panel_options = inject_panels())

###### USER ROUTES ###########

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
                session.permanent = True
                session["user"] = {'username': request.form['username'],
                                   'role': user['role'],
                                   'current_user': user.get('name','Unknown'),
                                   'team': user.get('team', 'Unassigned'),
                                   'rank': user.get('designation', 'Unassigned')}
                if user.get("status") != None:
                    user.pop("status")
                    db.save(user)
                return redirect(url_for('select_location'))
    else:
        pass
    session["user"] = None
    return render_template('user/login.html', error=error, requires_keyboard=True)

#Route to handle logging out
@app.route("/logout")
def logout():
    session["user"] = None
    session["location"] = None
    return render_template('user/login.html', requires_keyboard=True)

#route to main user management page
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
        if request.form['designation'] in ['Consultant', 'Intern','Registrar','Medical Student', 'Student Clinical Officer', "Clinical Officer","Visiting Doctor"] :
            provider["team"] = request.form["team"]
        else:
            provider["ward"] = request.form["wardAllocation"]
        db.save(provider)
    else:
      current_users = db.find({"selector": { "type": "user"}, "limit": 200})
      flash("Username already exists", 'error')
      return render_template("user/index.html", requires_keyboard=True, users =current_users)
    flash("New user created","success")
    return redirect(url_for("users"))

@app.route("/user/<user_id>/update_password", methods=["GET", "POST"])
def change_password(user_id=None):
    if request.method == "POST":
        user = db.get(user_id)
        if user == None:
            flash("User not found", 'error')
            return redirect(url_for("index"))
        else:
            user["password_hash"] =  generate_password_hash(request.form["password"])
            db.save(user)
            return redirect(url_for("index"))
    else:
        return render_template("user/update_password.html", requires_keyboard=True,username = user_id)

@app.route("/user/<user_id>/reset_password")
def reset_password(user_id=None):
    user = db.get(user_id)
    if user == None:
        flash("User not found", 'error')
        return redirect(url_for("index"))
    else:
        user["password_hash"] =  generate_password_hash(user.get("name").split(" ")[1].lower())
        db.save(user)
        return redirect(url_for("index"))

@app.route("/user/<user_id>/deactivate")
def deactivate_user(user_id=None):
    user = db.get(user_id)
    if user == None:
        flash("User not found", 'error')
        return redirect(url_for("index"))
    else:
        user["status"] =  "Deactivated"
        db.save(user)
        return redirect(url_for("users"))

@app.route("/user/<user_id>/activate")
def activate_user(user_id=None):
    user = db.get(user_id)
    if user == None:
        flash("User not found", 'error')
        return redirect(url_for("index"))
    else:
        user.pop("status")
        db.save(user)
        return redirect(url_for("users"))

@app.route("/select_location", methods=["GET", "POST"])
def select_location():
    error= None
    if request.method == "POST":
        if request.form['location'] == '' :
            flash("Invalid location. Please try again.", 'error')
            error = "Invalid location. Please try again."
        else:
            session["location"] = request.form['location']
            return redirect(url_for('index'))

    session["location"] = None
    return render_template('user/select_location.html', error=error, options=locations_options())

###### LAB ORDER ROUTES ###########
#create a new lab test order
@app.route("/test/create", methods=['POST'])
def create_lab_order():
    for test in request.form.getlist('test_type[]'):
        new_test = {
                'ordered_by': request.form['ordered_by'],
                'date_ordered': datetime.now().strftime('%s') ,
                'status': 'Ordered',
                'sample_type' : request.form['specimen_type'],
                'clinical_history': request.form['clinical_history'],
                'Priority':request.form['priority'],
                'ward': session["location"],
                'patient_id': request.form['patient_id']
            }
        if len(test.split("|")) > 1:
            new_test['tests'] = {}
            new_test['type'] =  "test panel"
            new_test["panel_type"] = test.replace( "|","")
            panel_details = db.get(new_test["panel_type"])
            if panel_details != None:
                for test in panel_details.get("tests"):
                    new_test['tests'][db.get(test)["test_type_id"]] = {}
        else:
             new_test['type'] =  'test'
             new_test['test_type'] = test
        db.save(new_test)
        flash("New test ordered.", 'success')
    return redirect(url_for('patient', patient_id=request.form['patient_id'], sample_draw=(request.form["sampleCollection"] == "Collect Now")))

#update lab test orders to specimen collected
@app.route("/test/<test_id>/collect_specimen")
def collect_specimens(test_id):
    tests = db.find({"selector" : {"type":{"$in": ["test","test panel"]}, "_id": {"$in": test_id.split("^")}}})
    test_ids = []
    test_names = []
    if tests == None or tests == []:
        return redirect( url_for("index", error = "Tests not found"))
    patient = db.get(tests[0]["patient_id"])
    dr = tests[0]["ordered_by"]
    wards = {"4A":"19","4B":"20","MSS":"44","MHDU":"56"}
    collected_at = datetime.now().strftime('%s')
    collection_id = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(2)) + collected_at

    for test in tests:
        test["status"] = "Specimen Collected"
        test["collected_by"] = session["user"]['username']
        test["collected_at"] = collected_at
        test["collection_id"] = collection_id
        if test["type"] == "test":
            test_ids.append(test["test_type"])
            test_names.append(db.find({"selector": {"type":"test_type","test_type_id": test["test_type"]}, "fields": ["short_name"]})[0]["short_name"])
            test_string = [patient["name"].replace(" ", "^"), patient["_id"], patient["gender"][0],
                     datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                     wards[tests[0]["ward"]] ,dr,tests[0]["clinical_history"],tests[0]["sample_type"],
                     datetime.now().strftime("%s"), ("^").join(test_ids), tests[0]["Priority"][0] ]
        else:
            panel = db.get(test["panel_type"])
            test_names.append(panel.get("short_name"))
            if panel.get("orderable"):
                test_ids.append(panel["panel_id"])
                test_string = [patient["name"].replace(" ", "^"), patient["_id"], patient["gender"][0],
                     datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                     wards[tests[0]["ward"]] ,dr,tests[0]["clinical_history"],tests[0]["sample_type"],
                     datetime.now().strftime("%s"), ("^").join(test_ids), tests[0]["Priority"][0],"P" ]
            else:
                for test_type_id in db.find({"selector": {"type":"test_type","_id": {"$in": panel["tests"]}}, "fields": ["test_type_id"]}):
                    test_ids.append(test_type_id.get("test_type_id"))

                test_string = [patient["name"].replace(" ", "^"), patient["_id"], patient["gender"][0],
                         datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                         wards[tests[0]["ward"]] ,dr,tests[0]["clinical_history"],tests[0]["sample_type"],
                         datetime.now().strftime("%s"), ("^").join(test_ids), tests[0]["Priority"][0]]
        db.save(test)

    labelFile = open("/tmp/test_order.lbl", "w+")
    labelFile.write("N\nq406\nQ203,027\nZT\n")
    labelFile.write('A5,10,0,1,1,2,N,"%s"\n' % patient["name"])
    labelFile.write('A5,40,0,1,1,2,N,"%s (%s)"\n' % (datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), patient["gender"][0]) )
    labelFile.write('b5,70,P,386,80,"%s$"\n' % ("~").join(test_string))
    labelFile.write('A20,170,0,1,1,2,N,"%s"\n' % (",").join(test_names))
    labelFile.write('A260,170,0,1,1,2,N,"%s" \n' % datetime.now().strftime("%d-%b %H:%M"))
    labelFile.write("P1\n")
    labelFile.close()
    os.system('sudo sh ~/print.sh /tmp/test_order.lbl')
    flash("Specimen collected.", 'success')
    return redirect(url_for('patient', patient_id=patient.get("_id")))

#update lab test orders to specimen collected
@app.route("/test/<test_id>/reprint")
def reprint_barcode(test_id):
    tests = db.find({"selector" : {"type":{"$in": ["test","test panel"]}, "collection_id":  test_id}})
    if tests == None or tests == []:
        tests = db.find({"selector" : {"type":{"$in": ["test","test panel"]}, "_id":  test_id }})
    test_ids = []
    test_names = []
    if tests == None or tests == []:
        return redirect( url_for("index", error = "Tests not found"))
    patient = db.get(tests[0]["patient_id"])
    dr = tests[0]["ordered_by"]
    wards = {"4A":"19","4B":"20","MSS":"44","MHDU":"56"}

    for test in tests:
        if test["type"] == "test":
            test_ids.append(test["test_type"])
            test_names.append(db.find({"selector": {"type":"test_type","test_type_id": test["test_type"]}, "fields": ["short_name"]})[0]["short_name"])
            test_string = [patient["name"].replace(" ", "^"), patient["_id"], patient["gender"][0],
                     datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                     wards[tests[0]["ward"]] ,dr,tests[0]["clinical_history"],tests[0]["sample_type"],
                     datetime.now().strftime("%s"), ("^").join(test_ids), tests[0]["Priority"][0] ]
        else:
            panel = db.get(test["panel_type"])
            test_names.append(panel.get("short_name"))
            if panel.get("orderable"):
                test_ids.append(panel["panel_id"])
                test_string = [patient["name"].replace(" ", "^"), patient["_id"], patient["gender"][0],
                     datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                     wards[tests[0]["ward"]] ,dr,tests[0]["clinical_history"],tests[0]["sample_type"],
                     datetime.now().strftime("%s"), ("^").join(test_ids), tests[0]["Priority"][0],"P" ]
            else:
                for test_type_id in db.find({"selector": {"type":"test_type","_id": {"$in": panel["tests"]}}, "fields": ["test_type_id"]}):
                    test_ids.append(test_type_id.get("test_type_id"))

                test_string = [patient["name"].replace(" ", "^"), patient["_id"], patient["gender"][0],
                         datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                         wards[tests[0]["ward"]] ,dr,tests[0]["clinical_history"],tests[0]["sample_type"],
                         datetime.now().strftime("%s"), ("^").join(test_ids), tests[0]["Priority"][0]]

    labelFile = open("/tmp/test_order.lbl", "w+")
    labelFile.write("N\nq406\nQ203,027\nZT\n")
    labelFile.write('A5,10,0,1,1,2,N,"%s"\n' % patient["name"])
    labelFile.write('A5,40,0,1,1,2,N,"%s (%s)"\n' % (datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), patient["gender"][0]) )
    labelFile.write('b5,70,P,386,80,"%s$"\n' % ("~").join(test_string))
    labelFile.write('A20,170,0,1,1,2,N,"%s"\n' % (",").join(test_names))
    labelFile.write('A260,170,0,1,1,2,N,"%s" \n' % datetime.now().strftime("%d-%b %H:%M"))
    labelFile.write("P1\n")
    labelFile.close()
    os.system('sudo sh ~/print.sh /tmp/test_order.lbl')

    return redirect(url_for('patient', patient_id=patient.get("_id")))


@app.route("/test/<test_id>/review_ajax")
@app.route("/test/<test_id>/review")
def review_test(test_id):
    test = db.get(test_id)
    if test.get("status") == "Analysis Complete":
        test["status"] = "Reviewed"
    else:
        test["status"] = "Specimen Rejected"
    test["reviewed_by"] = session["user"]['username']
    test["reviewed_at"] = datetime.now().strftime('%s')
    db.save(test)

    if "review_ajax" in request.path.split("/"):
        return "Success"
    else:
        return redirect(url_for('patient', patient_id=test['patient_id']))

###### MISC Functions ############

def get_test_measures(test, test_details):
    results = {}
    for measure in test.get("measures", []):
        if test_details["measures"].get(measure) == None:
            results[measure] = {"range": "", "interpretation":"Normal", "value": test["measures"][measure]}
        else:
            if test_details["measures"][measure].get("minimum") != None :
                results[measure] = {"range": test_details["measures"][measure].get("minimum") + " - " + test_details["measures"][measure].get("maximum")}
                results[measure]["value"] = re.sub(r'[^0-9\.]', '', test["measures"][measure])
                if results[measure]["value"] == "":
                    results[measure]["value"] = "Not Done"
                    results[measure]["interpretation"] = "Normal"
                elif float(results[measure]["value"]) < float(test_details["measures"][measure].get("minimum")):
                    results[measure]["interpretation"] = "Low"
                elif float(results[measure]["value"]) > float(test_details["measures"][measure].get("maximum")):
                    results[measure]["interpretation"] = "High"
                else:
                    results[measure]["interpretation"] = "Normal"
            else:
                results[measure] = {"range": "", "interpretation":"Normal", "value": test["measures"][measure]}

    return results
###### DB CALLS ################

def prescribers():
    providers = []
    users = db.find({"selector": {"type": "user", "role": "Doctor",
      "status": {"$exists": False}},"fields": ["_id", "name"], "limit": 100})
    for user in users:
        if len(user['name'].split(" ")) > 1:
            name = user['name'].split(" ")[0][0] + ". " + user['name'].split(" ")[1]
        else:
            name = user['name']
        providers.append([name, user['_id']])
    providers.sort()
    return providers

def locations_options():
    return [["MSS", "Medical Short Stay"], ["4A", "Medical Female Ward"], ["4B", "Medical Male Ward"], ["MHDU", "Medical HDU"]]

def specimen_type_map(type):
    tests = db.find({"selector": {"type": "test_type"},"fields": ["specimen_types"]})
    for i in tests:
        for t in i["specimen_types"]:
            if type == t:
                return i["specimen_types"][t]
    return "Unknown"

def inject_tests():
    options = {}
    tests = db.find({ "selector": {"type": "test_type"},"fields": ["_id","test_type_id","specimen_types"],"limit":500})
    for test in tests:
        options[test["test_type_id"]] =  {"name": test["_id"], "specimen_types" :test["specimen_types"].keys()}

    options = sorted(options.items(), key=lambda e: e[1]["name"])
    return options

def inject_specimen_types():
    tests = db.find({"selector": {"type": "test_type"},"fields": ["specimen_types"]})
    options = []

    for i in tests:
        for t in i["specimen_types"]:
            if [i["specimen_types"][t],t ] not in options:
                options.append([i["specimen_types"][t],t ])

    options.sort()
    return  [options[i * 2:(i + 1) * 2] for i in range((len(options) + 2 - 1) // 2 )]

def inject_panels():
    options = {}
    panels = db.find({ "selector": {"type": "panels"},"fields": ["_id","specimen_types"],"limit":500})
    for panel in panels:
        options[panel["_id"]] =  {"name": panel["_id"], "specimen_types" : panel["specimen_types"].keys()}
    options = sorted(options.items(), key=lambda e: e[1]["name"])
    return options


###### APPLICATION CALLBACKS ###########
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
    if not re.search("asset", request.path):
        initialize_connection()
        if settings["using_rpi"] == "True":
            if request.path == "/":
                ledControl().turn_led_on()
            else:
                ledControl().turn_led_off()

        if request.path != "/login" and request.path != "/logout":
            if session.get("user") == None:
                return redirect(url_for('login'))
            else:
                if session.get("location") == None and request.path != "/select_location":
                    return  redirect(url_for('select_location'))

###### APPLICATION CONTEXT PROCESSORS ###########
# Used to get data in views
@app.context_processor
def inject_now():
    return {'now': datetime.now().strftime("%H:%M%p")}

@app.context_processor
def inject_user():
    return {'current_user': session.get("user")}

@app.context_processor
def inject_message_category():
    return {'message_category': {"info":"#004085", "success":"#28a745", "error":"#dc3545","warning": "#ffc107"}}

@app.context_processor
def inject_power():
    if settings["using_rpi"] == "True":
        voltage = CheckVoltage().getVoltage()
        onCharge = False #CheckVoltage().isCharging()
        if voltage > 70:
            rating = "high"
        elif voltage > 30 and voltage < 70:
            rating = "medium"
        else:
            rating = "low"
    else:
        voltage=  100
        rating =  "high"
        onCharge = True
    return {"current_power": voltage, "power_class": rating, "charging": onCharge}

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
    app.run(port="7500", debug=True, host='0.0.0.0')
