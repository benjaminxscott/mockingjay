mockingjay
==========

A place to share breach data

## Setup
Get Dependencies
`pip install -r requirements.txt`

Create Database
```
python
import mockingjay
mockingjay.init_db()
```

Start server
`./mockingjay.py`

## Usage
Create a new incident by filling form fields at:
    http://$server/breaches/new

This endpoint accepts POST data as in:
`curl $server/breaches/new --data "submitter=MandiCorp&confidence=Low&description=Real Bad&asset=All Teh Secrets!&sensitive=False&organization=Jeffcorp"`
**note:** An HTTP 400 error is returned for invalid submissions

A breach ID will be returned to you along with a URL for the XML output at:
    $server/breaches/$id/stix
