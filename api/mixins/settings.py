import os
import secrets

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql://postgres:password@localhost:5432/mydatabase')
DATA_ROOT = os.getenv('DATA_ROOT', '/data/')
APP_ROOT = os.getenv('APP_ROOT', './')
IS_DEV = (APP_ROOT == './')
API_VERSION = '2.4.0'
SECRET_KEY = 'DEV_KEY' if IS_DEV else os.getenv('SECRET_KEY', secrets.token_urlsafe(128))