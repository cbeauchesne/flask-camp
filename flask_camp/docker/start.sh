#!/bin/bash
service nginx start
exec uwsgi --ini flask_camp/docker/uwsgi.ini
