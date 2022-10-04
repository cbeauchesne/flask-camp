#!/bin/bash

mkdir logs/
docker compose down
docker compose up --remove-orphans --wait -d redis pg
