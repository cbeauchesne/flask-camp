#!/bin/bash

export FLASK_MAIL_SUPPRESS_SEND=True
export FLASK_ERRORS_LOG_FILE=logs/errors.log
export FLASK_SECRET_KEY=not-secret
export FLASK_INIT_DATABASES=True
export FLASK_MAIL_DEFAULT_SENDER=do-not-reply@example.com
export FLASK_RATELIMIT_ENABLED=0
export FLASK_REDIS_HOST=redis
export FLASK_REDIS_PORT=6379

TARGET=fuzzer

docker-compose down
docker-compose up --remove-orphans --scale cms=3 -d
rm logs/*

curl http://localhost:5000/init_databases

python tests/end_tests/$TARGET/main.py

docker-compose logs haproxy > logs/haproxy.log
docker-compose logs redis > logs/redis.log

docker-compose down