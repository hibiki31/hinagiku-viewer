# ==============================
# Stage 1: ビルドステージ
# ==============================
FROM python:3.11-slim-bookworm AS builder

# pipのアップグレードと依存関係のインストール
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

# ==============================
# Stage 2: 実行ステージ
# ==============================
FROM python:3.11-slim-bookworm

# システムパッケージの更新とOpenCV実行に必要な最小限のライブラリをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ビルドステージからPythonパッケージをコピー
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリケーションディレクトリの作成
RUN mkdir -p /opt/app /opt/data

# アプリケーションコードのコピー
COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8000

# データベースマイグレーション実行後、gunicornを起動
CMD ["sh", "-c", "alembic upgrade head && gunicorn --config /opt/app/mixins/gnicorn_config.py"]
