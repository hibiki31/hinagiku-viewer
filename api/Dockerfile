FROM python:3.11-buster

RUN apt update && apt install -y libgl1-mesa-dev

COPY ./requirements.txt /tmp/
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/app
RUN mkdir -p /opt/data

COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8000

CMD ["gunicorn", "--config", "/opt/app/gnicorn_config.py"]