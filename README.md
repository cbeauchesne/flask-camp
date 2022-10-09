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

Then run the app : 
```bash
TODO dev env
flask --debug run
```

All possible endpoints with a short explanation are visible on root page: http://localhost:5000
