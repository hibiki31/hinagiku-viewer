from settings import GNICORN_WORKERS

wsgi_app = "main:app"
bind = '0.0.0.0:8000'

# ワーカープロセス数: (2 × CPUコア数) + 1 で動的設定
# 各ワーカーは独立したOSプロセスのためGILを回避でき、CPU-boundな画像変換を真に並列実行できる
workers = GNICORN_WORKERS

# UvicornWorker使用時の注意:
# gunicornの threads パラメータは syncワーカー(gthread等)にのみ有効。
# UvicornWorker は内部でuvicornのasyncioループを使用するため threads 設定は無視される。
# sync defエンドポイントの同時実行数はStarletteのスレッドプール上限(デフォルト40)に従う。
worker_class = 'uvicorn.workers.UvicornWorker'
reload = True
