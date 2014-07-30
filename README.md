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

> By default, process listens on port 8080 

## Usage
Create a new incident by filling form fields at:

    http://$server/breaches/new

This endpoint accepts POST data as in:

`curl $server/breaches/new --data "submitter=MandiCorp&confidence=Low&description=Real Bad&damage=User Data Loss&sensitive=False&organization=Jeffcorp&timestamp=2012-01-01"`

**note:** An HTTP 400 error is returned for invalid submissions

A breach ID will be returned to you along with a URL for the XML output at:
    $server/breaches/$id/stix
