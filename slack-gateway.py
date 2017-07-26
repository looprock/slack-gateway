#!/usr/bin/env python
from json import loads
from bottle import Bottle, request, abort, response
import os
import sys
from slacker import Slacker

# We take 3 options as environment variables
token = os.environ.get('token', None)
listenhost = os.environ.get('host', '0.0.0.0')
listenport = os.environ.get('port', '18080')

# we are useless withtout a slack token
if not token:
    print("ERROR: no token specified!")
    sys.exit(1)

# fire up slack and bottle app
slack = Slacker(token)
app = Bottle()

# we only have one route. It takes a JSON object containing:
# topic - OPTIONAL: prefix for message
# message - message content
# channels -  a list of one or more channels
# {"channels":["pager"], "message":"bwoop! bwoop! alert! alert!"}
# {"channels":["operations", "pager"], "topic":"monitoring", "message":"bwoop! bwoop! alert! alert!"}
@app.post('/', method='POST')
def index():
    postdata = request.body.read()
    data = loads(postdata)
    # we need these or the object is useless
    required = ['channels', 'message']
    for req in required:
        if req not in data:
            abort(422, "ERROR: missing required field %s!" % req)
    # append a 'topic' if there is one
    if 'topic' in data:
        msg = "%s - %s" % (data['topic'], data['message'])
    else:
        msg = data['message']
    # could optimize here with threads etc, but not necessary for my uses
    for channel in data['channels']:
        channel_string = "#%s" % (channel)
        slack.chat.post_message(channel_string, msg)

# this is a stub route because something in docker or docker for mac wants to talk to this route and it's constantly returning 404
@app.post('/inform', method='POST')
def inform():
    response.status = 200

# fire it up
if __name__ == '__main__':
    app.run(host=listenhost, port=listenport, server='tornado')
