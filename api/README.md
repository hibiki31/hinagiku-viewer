# API

## Alembic

```bash
docker-compose run api alembic upgrade head
alembic revision --autogenerate -m "Fix on delete"
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
