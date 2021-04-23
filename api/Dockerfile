FROM python:3.9.4-buster

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/app
RUN mkdir -p /opt/data
COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]