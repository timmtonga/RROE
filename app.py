#Written by Timothy Mtonga
#This is the main thread for the application

import os
from couchdb import Server
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template,redirect,session,flash,request,url_for
app = Flask(__name__, template_folder="views", static_folder="assets")

#Connect to a couchdb instance
couchConnection = Server('http://admin:rootpwd@127.0.0.1:5984/')

# Connect to a database or Create a Database
try:
    db = couchConnection['rroe_trial']
except:
    db = couchConnection.create('rroe_trial')

#Root page of application
@app.route("/")
def index():
    return render_template('main/index.html')

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
                session["user"] = {'username': request.form['username'], 'role': user['role'],
                                   'current_user': user['name'], 'team': user['team'], 'rank': user['designation']}
                return redirect(url_for('select_location'))

    session["user"] = None
    session["logged_in"] = None
    return render_template('user/login.html', error=error)

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
def patient():
    return render_template('patient/show.html')

@app.route("/user/new")
def new_user():
    return "New User Page"

@app.route("/user/create", methods=["Post"])
def create_user():
    #password_hash = generate_password_hash("request.form['password']")
    return "New user created"

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
    return {'current_user': {"username": "root", "name": "Dr Muzatifuna Wapulumuka "}}

@app.context_processor
def inject_patient():
    return {'patient': {"npid": "P000-018", "name": "John Doe", "age": "23 years"}}

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
