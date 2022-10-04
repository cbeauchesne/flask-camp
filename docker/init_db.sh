#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER wiki_api_user WITH PASSWORD 'wiki_api_user';
	CREATE DATABASE wiki_api;
	GRANT ALL PRIVILEGES ON DATABASE wiki_api TO wiki_api_user;
EOSQL
