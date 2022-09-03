import secrets

from flask import Flask
from flask_login import LoginManager
from flask_restful import Api

from . import database
from .views.healthcheck import HealthCheck
from .views.user import Users, UserValidation, UserLogin, UserLogout
from .views.document import DocumentsView, DocumentView


class Application(Flask):
    def __init__(self, **kwargs):
        super().__init__(__name__)

        sql_echo = kwargs.pop("sql_echo", False)

        self.config.from_object(kwargs)

        self._api = Api(self, catch_all_404s=True)
        self._login_manager = LoginManager(self)
        self.secret_key = secrets.token_hex()

        @self.login_manager.user_loader
        def load_user(user_id):
            from .models.user import User as UserModel

            return UserModel.get(id=int(user_id))

        @self.teardown_appcontext
        def shutdownsession(exception=None):
            database.session.remove()

        self.add_resource(HealthCheck, "/healthcheck")

        self.add_resource(Users, "/users")
        self.add_resource(UserValidation, "/validate_user/<int:user_id>")
        self.add_resource(UserLogin, "/login")
        self.add_resource(UserLogout, "/logout")

        self.add_resource(DocumentsView, "/documents")
        self.add_resource(DocumentView, "/document/<int:id>")

    def add_resource(self, *args, **kwargs):
        self._api.add_resource(*args, **kwargs)

    def create_all(self):
        database.create_all()
