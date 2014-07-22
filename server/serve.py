#!/usr/bin/env python

from flask import Flask, request, url_for, render_template, g, abort # 'g' is a magical database thingie
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

def insert_db(table, fields=(), values=()):
    # g.db is the database connection
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
    rowid = insert_db("breaches", ("submitter",), (request.form['submitter'],)) #trailing commas for tuples

    # TODO add error checking and return 400 if so
        # return None from this function if was error
    # TODO build URL for the breach - find_url = url_for ('breach', breach_id=new_id )
    # return tuple for id, url 
    return rowid

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
        breach_id = store_breach()
        print breach_id
        return render_template("display.html",status="success",breach_id=breach_id)
    
    return render_template("display.html")

@app.route('/breach/<int:breach_id>')
def get_breach(breach_id):
    return "details on a given breach " + str(breach_id)

@app.route('/breach/<int:breach_id>/stix')
def produce_stix(breach_id):
    db = get_db()
    result = query_db('select * from breaches where id = ?',
                [request.form['breach_id']], one=True)
    # TODO why no result for valid id query

    if result is None:
        abort(400) # kick error if no results
    else:
        pkg = GenerateIncident.build_stix(submitter)
        return pkg.to_xml()

if __name__ == '__main__':
# XXX add (host=$myip) to serve online
    app.run()
