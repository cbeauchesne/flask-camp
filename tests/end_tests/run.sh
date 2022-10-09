#!/bin/bash

export FLASK_MAIL_SUPPRESS_SEND=True
export FLASK_SECRET_KEY=not-secret
export FLASK_MAIL_DEFAULT_SENDER=do-not-reply@example.com
export FLASK_RATELIMIT_ENABLED=0
export FLASK_REDIS_HOST=redis
export FLASK_REDIS_PORT=6379

TARGET=fuzzer

rm -rf logs/*
touch logs/errors.log

docker compose up --remove-orphans --force-recreate --wait --scale app=3 -d

# calling this script directly will create the DB
docker compose exec app python app.py

PYTHONPATH=. python tests/end_tests/$TARGET/main.py

docker compose logs haproxy > logs/haproxy.log
docker compose logs redis > logs/redis.log
docker compose logs app > logs/app.log

docker compose down

python tests/end_tests/fuzzer/pretty.py
