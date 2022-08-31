import secrets

from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .views.healthcheck import HealthCheck


class Application(Flask):
    def __init__(self, user_model):
        super().__init__(__name__)
        self.user_model = user_model
        self._api = Api(self, catch_all_404s=True)
        self._login_manager = LoginManager(self)
        self.secret_key = secrets.token_hex()

        def before_request(*args, **kwargs):
            database.current_session = database.get_session()

        def after_request(response):
            database.current_session.close()
            return response

        @self.login_manager.user_loader
        def load_user(user_id):
            return self.user_model.get(id=int(user_id))

        self.before_request(before_request)
        self.after_request(after_request)

        database.connect()

        self.add_resource(HealthCheck, "/healthcheck")

    def add_resource(self, *args, **kwargs):
        self._api.add_resource(*args, **kwargs)

    def create_all(self):
        from .models import BaseModel

        BaseModel.metadata.create_all(bind=database._connection)


class _DataBase:
    def __init__(self):
        self._connection = None
        self.current_session = None

    def connect(self):
        self._connection = create_engine("sqlite://")

    def get_session(self, autocommit=False):
        return Session(self._connection, autocommit=autocommit)

    def execute(self, sql):
        return self._connection.execute(sql)


database = _DataBase()
