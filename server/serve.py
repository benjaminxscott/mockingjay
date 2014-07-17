#!/usr/bin/env python

from flask import Flask, request, url_for, render_template

app = Flask(__name__)

# ----- REAL LOGIC -----

def store_breach():
    new_id = 1337 # TODO generate uuid, pass to create_stix to maintain same one in stix output for 'incident'
    find_url = url_for ('breach', breach_id=new_id )
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
    # present input form on GET, or parse incoming POST data
    if request.method == 'POST':
    # TODO directly submit entered data
        status = store_breach()
        return render_template("display.html",status=status)
    
    return render_template("display.html")


@app.route('/breach/<int:breach_id>')
def each_breach_deets(breach_id):
    return "details on a given breach " + str(breach_id)

@app.route('/breach/<int:breach_id>/stix')
def produce_stix(breach_id):
    return "stix for a given breach"

if __name__ == '__main__':
# XXX add (host=$myip) to serve online
    app.debug = True # reload on src edits
    app.run()

'''
        - when did it happen?
        - What was stolen or disrupted? type of asset as AssetTypeVocab
        - how sure are you? as confidence (low, med, high) 
        - do you want to share with other affected organizations? (default sensitive handling - only submitee knows it)
        - reporter name as Reporter 
        - description as prose
        - organization name as Victim
'''
