import os
import re
import secrets

API_VERSION = '3.17.2'

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql://postgres:password@localhost:5432/mydatabase')
DATA_ROOT = re.sub(r"/$", "", os.getenv('DATA_ROOT', '/opt/data/'))
APP_ROOT = re.sub(r"/$", "", os.getenv('APP_ROOT', '/opt/app/'))
IS_DEV = bool(os.getenv('IS_DEV', ''))
DEBUG_LOG = bool(os.getenv('DEBUG_LOG', ''))
# Gunicornワーカープロセス数: 推奨式 (2 × CPUコア数) + 1
# 各ワーカーは独立プロセスのためGILを回避し、CPU-boundな画像変換を並列実行できる
GNICORN_WORKERS = (2 * (os.cpu_count() or 1)) + 1

CONVERT_THREAD = int(os.cpu_count())
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(128))
