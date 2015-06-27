#!/usr/bin/env python

import os
from datetime import datetime
from flask import make_response, Flask, request, url_for, render_template, abort 

from stix.core import STIXPackage
from generators import generateIncident
from utils.dbUtils import *

app = Flask(__name__)

# ----- APPLICATION LOGIC -----

def store_incident():
    # derive priority from attribs
    # lower = more urgent
    pri = 5 #least important
    if request.form['confidence']  == "High":
        pri = pri -1

    if request.form['sensitive'] :
        pri = pri -1

    td =  datetime.today() -datetime.strptime( request.form['timestamp'],"%Y-%m-%d" )
    if td.days <= 90: #if happened in last three months
        pri = pri -1

    # add to DB
    try:
        incident_id = insert_db("incidents", ("asset", "responder", "coordinator", "status",
                                              "submitter", "intent", "discovery", "description","damage",
                                              "sensitive", "organization", "confidence", "timestamp", "priority")
        , (
           request.form['asset'],
           request.form['responder'],
           request.form['coordinator'],
           request.form['status'],
           request.form['submitter'],
           request.form['intent'],
           request.form['discovery'],
           request.form['description'],
           request.form['damage'],
           request.form['sensitive'],
           request.form['organization'],
           request.form['confidence'],
           request.form['timestamp'],
           pri #priority
        ))
    except IntegrityError:
        incident_id = None

    return incident_id

# ----- URL ROUTING -----
@app.route('/about')
def landing():
    return render_template("about.html", about = True)

@app.route('/incident/list')
def list_incidents():
    result = query_db('select * from incidents')

    return render_template("incidentList.html", show_all = True, output = result)

@app.route('/incident/new', methods=['GET','POST'])
@app.route('/', alias = True)
def add_incident():
    # present input form or parse incoming POST data
    if request.method == 'POST':
        incident_id = store_incident()
        if incident_id is None:
            abort(400)
        else:
            # success msg and link to tracking 
            return render_template("incident.html",incident_id=incident_id)

    return render_template("incident.html")

@app.route('/incident/<int:incident_id>')
def incident_results(incident_id):
    result = query_db('select * from incidents where id = ?',
                [incident_id], one=True)

    if result is None:
        abort(400) # kick error if no results
    else:
        pkg = generateIncident.build_stix(result)
        xmlpkg = pkg.to_xml()

        fmt = request.args.get("format")
        if fmt == "stix":
            # make them download the xml file
            response = make_response(xmlpkg)
            response.headers['Content-Disposition'] = 'attachment;' + " filename=stix_incident-" + str(incident_id) + ".xml"
            response.headers['Content-Type'] = 'application/xml'
            return response

    return render_template("incidentList.html", show_one = True, output = result)


if __name__ == '__main__':
    app.debug = "True"
    app.run(host='0.0.0.0', port=8080)
