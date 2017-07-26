#!/usr/bin/env python
# version: 2.0.0
# http://docs.python.org/library/email.message.html
# http://docs.python.org/library/email-examples.html
import sys
import email
import requests
import json
import getopt
import logging

logging.basicConfig()


def usage():
    print sys.argv[0] + """ [options] [argument]
    options:

    -h/--help         -  print usage summary
    -d/--debug        -  print debug output
    -s/--subjectonly  -  only send the subject of the email, not the entire body
    -t/--topic=       -  specify the topic (default: email)
    -c/--channel=     -  send to a particular channel via the gateway (default: no channel specified)
    -g/--gateway=     -  specify the gateway ip/hostname (default: 127.0.0.1)
    -p/--gatewayport= -  specify the gateway port (default:18080)
"""

# setup
# put this script somewhere
# configure the URL parameter below
# install this script on a local or remote system with a mail server
# add to /etc/aliases:
# slack: "|/path/to/email-to-slack.py <options>"
# run newaliases
# you're done. Now sending mail to slack@host should send it through the gateway

debug = False
gateway = "127.0.0.1"
gatewayport = "18080"
subjectonly = False
topic = "email"
channel = ""

try:
    opts, remainder = getopt.gnu_getopt(sys.argv[1:], "hdsc:t:g:p:", ["help", "debug", "subjectonly", "channel=", "topic=", "gateway=", "gatewayport="])
except getopt.GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit()
    elif opt in ("-d", "--debug"):
        debug = True
    elif opt in ("-s", "--subject-only"):
        subjectonly = True
    elif opt in ("-t", "--topic"):
        topic = arg
    elif opt in ("-c", "--channel"):
        channel = arg
    elif opt in ("-g", "--gateway"):
        gateway = arg
    elif opt in ("-p", "--gatewayport"):
        gatewayport = arg


def degbu(string):
    if debug:
        print "DEBUG: %s" % string


# slack gateway
url = "http://%s:%s/%s" % (gateway, gatewayport, channel)
degbu("Url: %s" % url)


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

if subjectonly:
    data = msgsubject
else:
    data = """Message date: %s\n
    Message from: %s\n
    Message subject: %s\n
    Message body:\n
    %s\n\n""" % (msgdate, msgfrom, msgsubject, load)

if debug:
    print data

payload = {"topic": topic, "message": data}
degbu("payload:")
if debug:
    print payload

r = requests.post(url, data=json.dumps(payload))
degbu(r.status_code)
