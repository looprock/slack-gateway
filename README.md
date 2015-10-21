# slack-gateway
a logstash http output compatible slack api gateway

## Installation

pip install -r requirements.txt

##POSTing to slack-gateway

### URL

send to your default channel via: http://your.endpoint.com:18080

send to a different channel via http://your.endpoint.com:18080/differentchannel

### JSON object

topic / host - prefix for message

message - message content

channels - optional channels (additional to default/path defined channel)

```
{"topic": "test", "message": "test with channels as a string"}

{"topic": "test", "message": "test with channels as a string", "channels": "random"}

{"host": "test", "message": "test with channels as a string", "channels": "random"}

{"topic": "test", "message": "test with channels as a string", "channels": ["random","general"]}
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

I run this under supervisord to daemonize it.
