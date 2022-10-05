#!/bin/bash

rm -rf __pycache__
rm -rf .pytest_cache
rm -rf htmlcov
rm -rf logs
rm -rf prof
rm -rf .coverage
rm -rf flask_camp.egg-info
rm -rf dist

mkdir logs/