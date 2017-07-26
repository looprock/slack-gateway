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

# email-to-slack.py

```
options:

-h/--help         -  print usage summary
-d/--debug        -  print debug output
-s/--subjectonly  -  only send the subject of the email, not the entire body
-t/--topic=       -  specify the topic (default: email)
-c/--channel=     -  send to a particular channel via the gateway (default: no channel specified)
-g/--gateway=     -  specify the gateway ip/hostname (default: 127.0.0.1)
-p/--gatewayport= -  specify the gateway port (default:18080)
```

1. put the script somewhere

2. install this script on a local or remote system with a mail server
3. add to /etc/aliases RE:

slack: "|/path/to/email-to-slack.py <options>"

4. run newaliases

5. you're done. Now sending mail to slack@host should send it through the gateway
