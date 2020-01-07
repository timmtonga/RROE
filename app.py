#Written by Timothy Mtonga
#This is the main thread for the application

import os
import json
from couchdb import Server
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template,redirect,session,flash,request,url_for
app = Flask(__name__, template_folder="views", static_folder="assets")

config_file = "config/application.config"
settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

#Connect to a couchdb instance
couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"],settings["couch"]["passwd"],
                          settings["couch"]["host"],settings["couch"]["port"]))

# Connect to a database or Create a Database
try:
    db = couchConnection['rroe_trial']
except:
    db = couchConnection.create('rroe_trial')

#Root page of application
@app.route("/")
def index():
    records = []
    my_team_recs = []
    if session["user"]["role"] == "Nurse":
        for item in db.view('_design/tests/_view/testStatus'):
            if (item.value['status'] in ['Ordered', 'Specimen Collected', 'Analysis Complete'] and item.value['ward'] == session.get('location')):
                records.append({'status': item.value.get('status'),'test': item.value.get('test_type'),
                                'name': db.get(item.value.get('patient_id')).get('name'),
                                'ordered_on':datetime.fromtimestamp(float(item.value.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                                'patient_id': item.value.get('patient_id')})
    else:
        for item in db.view('_design/tests/_view/testByOrderer',key='doctor16'):
             records.append({'status': item.value.get('status'),'test': item.value.get('test_type'),
                             'name': db.get(item.value.get('patient_id')).get('name'),
                             'ordered_on':datetime.fromtimestamp(float(item.value.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                             'patient_id': item.value.get('patient_id')})

        my_team = []
        for provider in db.view("_design/users/_view/teams",key=session.get('user').get('team'), limit=1000):
            my_team.append(provider.value)

        for provider in my_team:
            for item in db.view('_design/tests/_view/testByOrderer',key=provider):
                my_team_recs.append({'status': item.value.get('status'),'test': item.value.get('test_type'),
                                'name': db.get(item.value.get('patient_id')).get('name'),
                                'ordered_by': db.get(provider).get('name'),
                                'ordered_on':datetime.fromtimestamp(float(item.value.get('date_ordered'))).strftime('%d %b %Y %H:%S'),
                                'patient_id': item.value.get('patient_id')})

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
    patient = db.get(patient_id)
    pt= { 'name': patient.get('name'), 'gender': 'male' if patient.get('gender') == 'M' else 'female',
          'dob': datetime.strptime(patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), 'id': patient_id}
    return render_template('patient/show.html',pt_details = pt, collect_sample=False)

#create a new lab test order
@app.route("/test/create", methods=['POST'])
def create_lab_order():
    print(request.form['patient_id'])
    print(request.form['specimen_type'])
    print(request.form['test_type[]'])
    print(request.form['clinical_history'])
    print(request.form['priority'])
    return redirect(url_for('patient', patient_id=request.form['patient_id']))

#update lab test orders to specimen collected
@app.route("/test/<test_id>/collect_specimen")
def collect_specimens(test_id=None):
    pat_id = 'DFOGLS'
    try:
        labelFile = open("/tmp/test_order.lbl", "w+")
        labelFile.write("N\nq406\nQ203,027\nZT\n")
        labelFile.write('A25,10,0,1,1,2,N,"James Phiri"\n')
        labelFile.write('A25,40,0,1,1,2,N,"2 Jul, 2019"\n')
        labelFile.write('b20,70,P,386,80,"James Phiri~XYXKRQ~M~19850115~4B~Dr Wangui~Septic Sores~201907111235~FBC^MPS^ESR~S"\n')
        labelFile.write('A25,120,0,1,1,2,N,"FBC, MPS & ESR"\n')
        labelFile.write("P1\n")
        labelFile.close()
        os.system('sh ~/print.sh /tmp/test_order.lbl')
    except:
        pass
    return redirect(url_for('patient', patient_id=pat_id))

#proces barcode from the main index page
@app.route("/process_barcode/<barcode>")
def barcode(barcode=None):
    #write function to handle different types of barcodes that we expect
    print(barcode)
    return render_template('user/login.html')

#Application callbacks
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
