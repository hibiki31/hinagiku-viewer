# API

## Alembic

```bash
docker-compose run api alembic upgrade head
alembic revision --autogenerate -m "Add is_favorite"
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

## 想定エラー

### OSError: [Errno 36] File name too long

ファイル名が長い場合、

```
Traceback (most recent call last):
  File "/workspace/api/tasks/library_import.py", line 59, in main
    book_import(send_book, user_model, db)
  File "/workspace/api/tasks/library_import.py", line 108, in book_import
    pre_model.page = make_thum(send_book, pre_model.uuid)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/api/mixins/convertor.py", line 117, in make_thum
    existing_zip.extract(cover_path, f"/tmp/hinav/")
  File "/usr/local/lib/python3.11/zipfile.py", line 1664, in extract
    return self._extract_member(member, path, pwd)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/zipfile.py", line 1727, in _extract_member
    os.makedirs(upperdirs)
  File "<frozen os>", line 225, in makedirs
```