import os

from flask import Flask
from werkzeug.middleware.profiler import ProfilerMiddleware

import flask_camp


app = Flask(__name__, static_folder=None)
app.config.update({"SECRET_KEY": "not very secret", "SQLALCHEMY_TRACK_MODIFICATIONS": False})
app.wsgi_app = ProfilerMiddleware(
    app.wsgi_app,
    restrictions=[
        os.path.dirname(flask_camp.__file__),
    ],
)

api = flask_camp.RestApi(app=app)

with app.app_context():
    api.database.create_all()
