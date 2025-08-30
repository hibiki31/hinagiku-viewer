from settings import GNICORN_WORKERS

wsgi_app = "main:app"
bind = '0.0.0.0:8000'
# リクエストを処理するワーカープロセスの数。
workers = GNICORN_WORKERS
# リクエストを処理するためのワーカー スレッドの数。指定された数のスレッドで各ワーカーを実行します。
threads = 1
worker_class = 'uvicorn.workers.UvicornWorker'
reload = True