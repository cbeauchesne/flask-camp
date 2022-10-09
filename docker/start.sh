#!/bin/bash
service nginx start
exec uwsgi --ini docker/uwsgi.ini
