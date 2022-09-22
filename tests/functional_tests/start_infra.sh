#!/bin/bash

export FLASK_MAIL_SUPPRESS_SEND=True
export FLASK_ERRORS_LOG_FILE=logs/errors.log
export FLASK_SECRET_KEY=not-secret
export FLASK_INIT_DATABASE=True
export FLASK_MAIL_DEFAULT_SENDER=do-not-reply@example.com

docker-compose up --scale cms=3
