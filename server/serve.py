#!/usr/bin/env python

from flask import Flask, request, url_for, render_template, g
from sqlite3 import dbapi2 as sqlite3

from stix.core import STIXPackage

import os
import GenerateIncident 

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mockingjay.db'),
    DEBUG=True))

# DOC - must run python -> import and init_db() to setup DB initially

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


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# ----- APPLICATION LOGIC -----

def store_breach():
    db = get_db()
    print request.form['submitter']
# TODO use sqlalchemy instead with a db.Model to handle uniq IDs
    query = 'INSERT into breaches values (?,?)'
    db.execute(query, (1337, request.form['submitter']))
    db.commit()

    # TODO build URL for the breach - find_url = url_for ('breach', breach_id=new_id )
    # return tuple or dict for id, url, status
    result = "success" 
    return result

# ----- URL ROUTING -----
@app.route('/about')
@app.route('/', alias = True)
def landing():
    return "Mockingjay says Hi!"

@app.route('/breach/list')
def list_breach():
    return "show all breaches"

@app.route('/breach/new', methods=['GET','POST'])
def add_breach():
    # present input form or parse incoming POST data
    if request.method == 'POST':
        status = store_breach()
        return render_template("display.html",status=status)
    
    return render_template("display.html")

@app.route('/breach/<int:breach_id>')
def get_breach(breach_id):
    return "details on a given breach " + str(breach_id)

@app.route('/breach/<int:breach_id>/stix')
def produce_stix(breach_id):
    # TODO query DB for ID and pass to func
    pkg = GenerateIncident.build_stix(breach_id)
    return pkg.to_xml()

if __name__ == '__main__':
# XXX add (host=$myip) to serve online
    app.run()
