# slack-gateway
a logstash http output compatible slack api gateway

## why?

I was trying to get a few things out of this service:

1. submit to multiple channels from a single endpoint

2. not have to expose and maintain the slack api endpoint in multiple applications

3. do different things with different types of data

## Installation

### Environment variables
token - your slack token, default: None
host - OPTIONAL: the IP to listen on, default: 0.0.0.0
port - OPTIONAL: the port to listen on, default: 18080


### Manual setup
pip install -r requirements.txt

copy slack-gateway.py to /usr/local/bin (or something)

token=x0x0-some-bogus-string /usr/local/bin/slack-gateway.py

I run this under something like supervisord to daemonize it.

### Docker build
docker build -t some/slack-gateway .

docker run -it -p 8080:8080 -e token=x0x0-some-bogus-string some/slack-gateway

### Docker pull

docker pull looprock/slack-gateway

##POSTing to slack-gateway

### URL

send to your default channel via: http://your.endpoint.com:18080

### JSON object

topic - OPTIONAL: prefix for message

message - message content

channels -  a list of one or more channels

```
{"topic": "test", "message": "test with channels as a list", "channels": ["random","general"]}
```
