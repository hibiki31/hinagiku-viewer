import os


DATA_ROOT = os.getenv('DATA_ROOT', './data/')
APP_ROOT = os.getenv('APP_ROOT', './')
IS_DEV = (APP_ROOT == './')