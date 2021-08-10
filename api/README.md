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

```
docker-compose run api alembic upgrade head
alembic revision --autogenerate
alembic upgrade head
alembic downgrade base
```