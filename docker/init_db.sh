#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER cms_user WITH PASSWORD 'cms_user';
	CREATE DATABASE cms;
	GRANT ALL PRIVILEGES ON DATABASE cms TO cms_user;
EOSQL
