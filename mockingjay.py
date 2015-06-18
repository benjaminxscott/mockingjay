#!/usr/bin/env python

import os
from datetime import datetime
from utils.dbUtils import *
import stix
import stix_edh

from stix.core import STIXPackage
import GenerateIncident

# ----- APPLICATION LOGIC -----

def store_breach():
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
        breach_id = insert_db("breaches", ("asset", "submitter",'description','damage','sensitive','organization','confidence','timestamp', 'priority')
        , (
          request.form['asset'] # what did they steal - text
        , request.form['submitter'] # who is posting this - text
        , request.form['description'] # what happened - text
        , request.form['damage'] # what did it impact - text
        , request.form['sensitive'] # is it secretive - boolean
        , request.form['organization'] # who was the victim - text
        , request.form['confidence'] # how sure are they - high/med/low/unknown
        , request.form['timestamp'] # when they submitted it - Y/m/d
        , pri #priority
        ))
    except IntegrityError:
        breach_id = None

    return breach_id

# ----- URL ROUTING -----
@app.route('/about')
def landing():
    return render_template("about.html", about = True)

@app.route('/breach/list')
def list_breaches():
    result = query_db('select * from breaches')

    return render_template("breachList.html", show_all = True, output = result)

@app.route('/breach/new', methods=['GET','POST'])
@app.route('/', alias = True)
def add_breach():
    # present input form or parse incoming POST data
    if request.method == 'POST':
        breach_id = store_breach()
        if breach_id is None:
            abort(400)
        else:
            # success msg and link to tracking 
            return render_template("breach.html",breach_id=breach_id)

    return render_template("breach.html")

@app.route('/breach/<int:breach_id>')
def breach_results(breach_id):
    result = query_db('select * from breaches where id = ?',
                [breach_id], one=True)

    if result is None:
        abort(400) # kick error if no results
    else:
        pkg = GenerateIncident.build_stix(result)
        xmlpkg = pkg.to_xml()

        fmt = request.args.get("format")
        if fmt == "stix":
            # make them download the xml file
            response = make_response(xmlpkg)
            response.headers['Content-Disposition'] = 'attachment;' + " filename=stix_breach-" + str(breach_id) + ".xml"
            response.headers['Content-Type'] = 'application/xml'
            return response

    return render_template("breachList.html", show_one = True, output = result)


if __name__ == '__main__':
    app.debug = "True"
    app.run(host='0.0.0.0', port=8080)
