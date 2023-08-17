FROM python:3.11-buster

RUN apt update && apt install -y libgl1-mesa-dev

COPY ./requirements.txt /tmp/
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/app
RUN mkdir -p /opt/data

COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8888

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]