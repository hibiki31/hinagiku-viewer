FROM python:3-buster

COPY ./requirements.txt /tmp/
RUN pip3 install --upgrade pip && pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/app
RUN mkdir -p /opt/data

COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8000

CMD ["gunicorn", "--config", "/opt/app/mixins/gnicorn_config.py"]