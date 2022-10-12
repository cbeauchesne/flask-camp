import logging

from flask import Flask
from flask_camp import RestApi


app = Flask(__name__, static_folder=None)
app.config.update({"SECRET_KEY": "not very secret", "SQLALCHEMY_TRACK_MODIFICATIONS": False})
app.config.from_prefixed_env()

handler = logging.FileHandler("logs/testing_errors.log")
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)  # pylint: disable=no-member

api = RestApi(app=app)

if __name__ == "__main__":
    with app.app_context():
        api.database.create_all()
