#!/bin/bash

set -e

docker compose up --remove-orphans --wait -d redis pg
