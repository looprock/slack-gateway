#!/usr/bin/python
import json
import requests
from bottle import Bottle, response, request, route, run, abort
from sets import Set

app = Bottle()

debug = False
slackbaseurl = "https://your.slack.com/services/hooks/slackbot?token=XXXX&channel=%23"
defaultchannel = "notifications"

def bug(msg):
    if debug:
        print "DEBUG: %s" % msg

@app.post('/', method='POST')
@app.post('/<channel>', method='POST')
def index(channel=defaultchannel):
    channels = Set([channel])
    postdata = request.body.read()
    if debug:
        print "DEBUG:"
        print postdata
    try:
        data = json.loads(postdata)
        if 'host' in data:
            topic = data['host']
        elif 'topic' in data:
            topic = data['topic']
        if 'channels' in data:
            bug("Found channels in data")
            if debug:
                print channels
            if isinstance(data['channels'], basestring):
                bug("channels is a string")
                channels.add(data['channels'])
            else:
                bug("channels is not a string")
                for i in data['channels']:
                    bug("adding %s to channels" % i)
                    channels.add(i)
        payload = "%s: %s" % (topic, data['message'])
        if debug:
            print channels
        for c in channels: 
            url = slackbaseurl + c
            bug("url - %s" % url)
            r = requests.post(url, data=payload)
    except:
        abort(500, "Invalid JSON object!.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='18080', debug=True, server='tornado')
