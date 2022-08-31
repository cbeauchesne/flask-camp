import secrets

from flask import Flask
from flask_restful import Api
from flask_login import LoginManager

from .database import database
from .views.healthcheck import HealthCheck
from .views.user import Users, UserValidation, UserLogin, UserLogout


class Application(Flask):
    def __init__(self):
        super().__init__(__name__)
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
            from .models.user import User as UserModel

            return UserModel.get(id=int(user_id))

        self.before_request(before_request)
        self.after_request(after_request)

        database.connect()

        self.add_resource(HealthCheck, "/healthcheck")

        self.add_resource(Users, "/users")
        self.add_resource(UserValidation, "/validate_user/<int:user_id>")
        self.add_resource(UserLogin, "/login")
        self.add_resource(UserLogout, "/logout")

    def add_resource(self, *args, **kwargs):
        self._api.add_resource(*args, **kwargs)

    def create_all(self):
        from .models import BaseModel

        BaseModel.metadata.create_all(bind=database._connection)
