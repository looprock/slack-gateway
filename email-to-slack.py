#!/usr/bin/env python
# version: 2.0.0
# http://docs.python.org/library/email.message.html
# http://docs.python.org/library/email-examples.html
import sys
import email
import requests
import json

# setup
# put this script somewhere
# configure the URL parameter below
# install this script on a local or remote system with a mail server
# add to /etc/aliases:
# slack: "|/path/to/email-to-slack.py"
# run newaliases
# you're done. Now sending mail to slack@host should send it through the gateway

# slack gateway
url = "http://[your_host_here]:18080"
debug = True


def degbu(string):
    if debug:
        print "DEBUG: %s" % string


def sanitize(txt):
    txt = txt.replace('"', '&quot;')
    txt = txt.replace("'", "&#039;")
    return txt

# read input from procmail
s = sys.stdin.read()
# parse message using the email module
msg = email.message_from_string(s)

if debug:
    print msg.is_multipart()

msgdate = msg['Date']
msgsubject = sanitize(msg['Subject'])
msgfrom = sanitize(msg['From'])
okcontent = ["text/plain", "text/html"]
if msg.is_multipart() is True:
    counter = 1
    load = ""
    for part in msg.walk():
        # multipart/* are just containers
        if part.get_content_maintype() == 'multipart':
            continue
        filename = part.get_filename()
        if part.get_content_type() in okcontent:
            load += sanitize(part.get_payload())
            load += "\n"
else:
    load = msg.get_payload()

load = sanitize(load.rstrip("\n"))

data = """Message date: %s\n
Message from: %s\n
Message subject: %s\n
Message body:\n
%s\n\n""" % (msgdate, msgfrom, msgsubject, load)

if debug:
    print data

payload = {"topic": "email", "message": data}
degbu("payload:")
if debug:
    print payload

r = requests.post(url, data=json.dumps(payload))
degbu(r.status_code)
