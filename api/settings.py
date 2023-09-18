import os
import re
import secrets

API_VERSION = '2.5.1'

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql://postgres:password@localhost:5432/mydatabase')
DATA_ROOT = re.sub(r"/$", "", os.getenv('DATA_ROOT', '/opt/data/'))
APP_ROOT = re.sub(r"/$", "", os.getenv('APP_ROOT', '/opt/app/'))
IS_DEV = bool(os.getenv('IS_DEV', False))
DEBUG_LOG = bool(os.getenv('DEBUG_LOG', False))

CONVERT_THREAD = int(os.cpu_count())
SECRET_KEY = 'DEV_KEY' if IS_DEV else os.getenv('SECRET_KEY', secrets.token_urlsafe(128))