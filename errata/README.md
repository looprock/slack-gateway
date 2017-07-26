# slack-gateway
a logstash http output compatible slack api gateway

## why?
I was trying to get a few things out of this service:

1. submit to multiple channels from a single endpoint

2. accept data from logstash from the default http plugin

3. not have to expose and maintain the slack api endpoint in multiple applications

4. do different things with different types of data

5. handle per-channel posting across multiple teams

## Installation

1. pip install -r requirements.txt

2. configure gateway.conf

3. start from the same directory as gateway.conf or point to gateway.conf via -c


##POSTing to slack-gateway

### URL

send to your default channel via: http://your.endpoint.com:18080

send to a different channel via http://your.endpoint.com:18080/differentchannel

### JSON object

topic / host - prefix for message

message - message content

channels - optional channels (additional to default/path defined channel)

```
{"topic": "test", "message": "this is just a topic test"}

{"host": "foo.bar.com", "message": "this is just a host test"}

{"host": "test", "message": "test with channels as a string", "channels": "random"}

{"topic": "test", "message": "test with channels as a list", "channels": ["random","general"]}
```

# from logstash

something like:

```
if [message] =~ "^ERROR" {
     http {
         url => "http://your.endpoint.com:18080"
         http_method => "post"
     }
 }
```

## running slack-gateway

I run this under supervisord to daemonize it.

```
[program:slack-gateway]
user=slack
directory=/opt/slack-gateway
command=/opt/slack-gateway/slack-gateway.py -c /opt/slack-gateway/gateway.conf
```
