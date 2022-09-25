#!/bin/bash

export FLASK_MAIL_SUPPRESS_SEND=True
export FLASK_ERRORS_LOG_FILE=logs/errors.log
export FLASK_SECRET_KEY=not-secret
export FLASK_INIT_DATABASE=True
export FLASK_MAIL_DEFAULT_SENDER=do-not-reply@example.com
export FLASK_RATELIMIT_ENABLED=0
export FLASK_REDIS_HOST=redis
export FLASK_REDIS_PORT=6379

docker-compose down
docker-compose up --scale cms=3 -d

python tests/functional_tests/main.py

docker-compose logs > logs/functional_tests.log
docker-compose down


