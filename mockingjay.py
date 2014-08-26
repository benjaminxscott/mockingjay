#!/usr/bin/env python

import os
from flask import make_response, Flask, request, url_for, render_template, g, abort # 'g' is a magical database thingie
from sqlite3 import dbapi2 as sqlite3
from sqlite3 import IntegrityError
from datetime import datetime

from stix.core import STIXPackage
import GenerateIncident 


app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mockingjay.db')
    ))

# ----- DATABASE CODE -----
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def insert_db(table, fields=(), values=()):
    db = get_db()
    cur = db.cursor()
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur.execute(query, values)
    db.commit()
    id = cur.lastrowid
    cur.close()
    return id

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

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
    return render_template("display.html", about = True)

@app.route('/breach/list')
def list_breaches():
    result = query_db('select * from breaches')

    return render_template("display.html", show_all = True, output = result)

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
            return render_template("display.html",breach_id=breach_id)
    
    return render_template("display.html")


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

    return render_template("display.html", show_one = True, output = result)


if __name__ == '__main__':
   app.debug = "True"
   app.run(host='0.0.0.0', port=8080)
