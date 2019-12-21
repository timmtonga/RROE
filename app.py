#Written by Timothy Mtonga
#This is the main thread for the application

import os
from datetime import datetime
from flask import Flask, render_template,redirect,session,flash,request
app = Flask(__name__, template_folder="views", static_folder="assets")

#Root page of application
@app.route("/")
def index():
    return render_template('main/index.html')

@app.route("/patient", methods=['GET'])
def patient():
    return render_template('patient/show.html')

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow().strftime("%d-%b-%y %H:%M")}

@app.context_processor
def inject_user():
    return {'current_user': {"username": "root", "name": "Dr Muzatifuna Wapulumuka "}}

@app.context_processor
def inject_patient():
    return {'patient': {"npid": "P000-018", "name": "John Doe", "age": "23 years"}}

if __name__ =='__main__':
    app.secret_key = os.urandom(25)
    app.run(port="7500", debug=True, host='0.0.0.0')
