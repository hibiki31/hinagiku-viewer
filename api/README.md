# API

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
alembic revision --autogenerate
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