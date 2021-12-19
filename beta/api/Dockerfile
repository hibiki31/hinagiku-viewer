FROM python:3.9.6-buster

RUN mkdir /app

WORKDIR /tmp

ADD requirements.txt /tmp/
RUN pip install -r requirements.txt

ADD . /app/

WORKDIR /app

CMD [ "uwsgi", "/app/uwsgi.ini" ]