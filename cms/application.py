import secrets

from flask import Flask
from flask_login import LoginManager
from flask_restful import Api

from . import database
from .models.user import User as UserModel
from .views.account import EmailValidationView, UserLoginView, UserLogoutView, ResetPasswordView
from .views.block_user import BlockUserView
from .views.changes import ChangesView
from .views.document import DocumentsView, DocumentView
from .views.healthcheck import HealthCheckView
from .views.log import LogsView
from .views.protection import ProtectionView
from .views.user import UsersView, UserView


class Application(Flask):
    def __init__(self, **kwargs):
        super().__init__(__name__)

        self.config.from_object(kwargs)

        self._api = Api(self, catch_all_404s=True)
        self._login_manager = LoginManager(self)
        self.secret_key = secrets.token_hex()

        @self.login_manager.user_loader  # pylint: disable=no-member
        def load_user(user_id):
            return UserModel.get(id=int(user_id))

        @self.teardown_appcontext
        def shutdownsession(exception=None):  # pylint: disable=unused-argument
            database.session.remove()

        self.add_resource(HealthCheckView, "/healthcheck")

        self.add_resource(UsersView, "/users")
        self.add_resource(UserView, "/user/<int:id>")

        self.add_resource(UserLoginView, "/login")
        self.add_resource(UserLogoutView, "/logout")

        self.add_resource(EmailValidationView, "/validate_email")
        self.add_resource(ResetPasswordView, "/reset_password")

        self.add_resource(DocumentsView, "/documents")
        self.add_resource(DocumentView, "/document/<int:id>")

        self.add_resource(ChangesView, "/changes")
        self.add_resource(LogsView, "/logs")

        self.add_resource(ProtectionView, "/protect/<int:id>")
        self.add_resource(BlockUserView, "/block_user/<int:id>")

    def add_resource(self, *args, **kwargs):
        self._api.add_resource(*args, **kwargs)

    def create_all(self):
        database.create_all()
