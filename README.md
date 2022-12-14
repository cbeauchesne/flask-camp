flask-camp is a flask extension that build an full featured (but generic) wiki REST API.

## Installation

```bash
pip install flask-camp
```

## Usage

```python
from flask import Flask
from flask_camp import RestApi

app = Flask(__name__)
api = RestApi(app)
```

## Run your app

You'll need a running [redis](https://redis.io/) on port 6379 and a [postgresql](https://www.postgresql.org/) on port 5432. If you don't have it, you can copy paste the docker-compose.yml file in this repo and just run `docker compose up -d`

```bash
flask --debug run
```

All possible endpoints with a short explanation are visible on root page: http://localhost:5000
