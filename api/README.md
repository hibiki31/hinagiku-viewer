# API

## コーディング規約

- 例外オブジェクトは再利用せず、HTTPExceptionにコードとメッセージを記述する


## Model

- user
  - id
  - password
- book
  - id
  - user_id
  - is_shared
  - name
- book_user
  - user_id
  - book_id
  - read_times
  - open_page
  - rate

## Alembic

```bash
docker-compose run api alembic upgrade head
alembic revision --autogenerate -m "Add cached status"
alembic upgrade head
# データリセット
alembic downgrade base
```

## Develop

```
apt update
apt install -y postgresql-client
psql -h db -U postgres -d mydatabase -f inset.sql
```

```
cp ../../data/hinav-dev-testdata/* ../../data/book_send/
```

## 起動

```
gunicorn --config ./gnicorn_config.py 
```

## マイグレーション参考

- https://zenn.dev/tk_resilie/articles/fastapi0100_pydanticv2
