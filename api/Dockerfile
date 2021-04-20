FROM python:3.8.6-buster

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install flake8 
RUN pip install autopep8

RUN pip install fastapi
RUN pip install uvicorn

RUN pip install databases
RUN pip install sqlalchemy
RUN pip install aiosqlite
RUN pip install fastapi-camelcase
RUN pip install requests==2.24.0
RUN pip install pandas==1.1.3
RUN pip install aiofiles
RUN pip install Pillow
RUN pip install alembic
RUN pip install fastapi-jwt-auth
RUN pip install passlib
RUN pip install python-multipart
RUN pip install bcrypt

RUN mkdir -p /opt/app
RUN mkdir -p /opt/data
COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]