FROM alpine
MAINTAINER Doug Land <dland@ojolabs.com>

copy requirements.txt /tmp/

RUN \
  apk update \
  && apk add python py-pip build-base python-dev libffi-dev openssl-dev \
  && pip install -r /tmp/requirements.txt \
  && apk del build-base \
  && rm -rf /var/cache/apk/*

COPY slack-gateway.py /usr/local/bin/slack-gateway.py
CMD /usr/bin/python /usr/local/bin/slack-gateway.py
