set -eu

alembic downgrade base
alembic upgrade head

rm -rf ./.data-dev/book*
mkdir -p ./.data-dev/book_send
cp -rv ./.data-dev/test_data/* ./.data-dev/book_send