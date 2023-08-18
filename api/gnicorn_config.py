import os

wsgi_app = "main:app"
bind = '0.0.0.0:8000'
workers = 2 * os.cpu_count() + 1
threads = 2 * os.cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'
reload = True