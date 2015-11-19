#!/usr/bin/env python
import json
import requests
from bottle import Bottle, request, abort
from sets import Set
import re
import time
import logging
import os
import getopt
import sys

logging.basicConfig()


def usage():
    print sys.argv[0] + """ [options] [argument]
    options:

    -h/--help         -  print usage summary
    -d/--debug        -  print debug output
    -c/--conf         -  configuration file to use
"""


def printtime():
    return time.strftime('%Y-%m-%dT%H:%M:%S%Z', time.localtime())


def bug(msg):
    if debug:
        print "DEBUG: %s" % msg


def countnagios(message):
    bug("found topic nagios")
    bug("message: %s" % message)
    if re.search('\\\*\\\* PROBLEM', message):
        tmp = message.split("** PROBLEM Service Alert: ")[1].split(" is ")[0].replace(".", "-").replace(" ", "-").split("/")
        smap = "alerts.%s.%s" % (tmp[0], tmp[1])
        bug("incrementing: %s" % smap)
        sdout = statsd.incr(smap)
        bug("sdout %s" % str(sdout))
        bug("%s updated" % smap)


def counttest(message):
    # you can use the topic 'test' to trigger a count of alerts.testmessage metric to validate your statsd setup
    bug("found topic test")
    bug("message: %s" % message)
    smap = "alerts.testmessage"
    bug("incrementing: %s" % smap)
    sdout = statsd.incr(smap)
    bug("sdout %s" % str(sdout))
    bug("%s updated" % smap)


def countrundeck(message):
    bug("found topic rundeck")
    bug("message: %s" % message)
    mtype = message.split(",")[0].strip()
    if mtype == 'succeeded':
        pre = 'status'
    else:
        pre = 'alerts'
    smap = "%s.rundeck.%s" % (pre, mtype)
    bug("incrementing: %s" % smap)
    sdout = statsd.incr(smap)
    bug("sdout %s" % str(sdout))
    bug("%s updated" % smap)


def getmetrics(topic, message):
    if topic == 'nagios':
        countnagios(message)
    elif topic == 'test':
        counttest(message)
    elif topic == 'rundeck':
        countrundeck(message)


cmddebug = False
cmdconf = False

try:
    opts, remainder = getopt.gnu_getopt(sys.argv[1:], "hdc:", ["help", "debug", "conf="])
except getopt.GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit()
    elif opt in ("-d", "--debug"):
        cmddebug = True
    elif opt in ("-c", "--conf"):
        cmdconf = arg


app = Bottle()

_basedir = os.path.abspath(os.path.dirname(__file__))
testpath = "%s/gateway.conf" % (_basedir)
if os.path.exists(testpath):
    logging.debug(" %s found config in local dir, using that: %s" % (printtime(), testpath))
    conffile = testpath

if cmdconf:
    logging.debug(" %s found config in command line, using that: %s" % (printtime(), cmdconf))
    conffile = cmdconf

if not conffile:
    logging.critical(" %s no configuration found or specified!" % (printtime()))
    sys.exit(1)


if os.path.exists(conffile):
    logging.debug(" %s reading conffile %s" % (printtime(), conffile))
    f = open(conffile)
    try:
        data = f.read()
    finally:
        f.close()
else:
    logging.critical(" %s config %s not found!" % (printtime(), conffile))
    sys.exit(1)

conf = json.loads(data)

if cmddebug:
    debug = cmddebug
else:
    debug = bool(conf['debug'])

if bool(conf['statsd']['enabled']):
    from statsd import StatsClient
    if bool(conf['statsd']['prefix']):
        statsd = StatsClient(host=conf['statsd']['server'], port=int(conf['statsd']['port']), prefix=conf['statsd']['prefix'])
    else:
        statsd = StatsClient(host=conf['statsd']['server'], port=int(conf['statsd']['port']))
    logging.debug(" %s statsd reporting enabled" % printtime())


@app.post('/', method='POST')
@app.post('/<channel>', method='POST')
def index(channel=conf['default_channel']):
    channels = Set([channel])
    postdata = request.body.read()
    if debug:
        print "DEBUG:"
        print postdata
    try:
        data = json.loads(postdata)
        if debug:
            print "DEBUG: data - "
            print data
        if 'host' in data:
            topic = data['host']
        elif 'topic' in data:
            topic = data['topic']
        bug("Found topic: %s" % topic)
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
        if debug:
            print "Channels:"
            print channels
        payload = "%s: %s" % (topic, data['message'])
        bug("payload: %s" % payload)
        # send nagios metrics to statsd
        if bool(conf['statsd']['enabled']):
            getmetrics(topic, data['message'])
        for c in channels:
            if c in conf['channelmap'].keys():
                url = conf['channelmap'][c] + c
            else:
                url = conf['channelmap']['default'] + c
            bug("url - %s" % url)
            requests.post(url, data=payload)
    except:
        abort(500, "Error submitting to slackbot!")


# this is just a test route to see what's getting posted
@app.post('/print', method='POST')
def postprint():
    postdata = request.body.read()
    print postdata

if __name__ == '__main__':
    app.run(host=conf['gateway']['host'], port=conf['gateway']['port'], debug=debug, server='tornado', reloader=conf['gateway']['reload_config'])
