#!/bin/bash

git pull
docker-compose build
docker-compose down
docker-compose up -d
docker-compose run api alembic upgrade head
docker restart nginx_nginx-proxy_1