from functools import wraps
import logging
import secrets

from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from werkzeug.exceptions import Forbidden, BadRequest

from . import database
from .models.user import User as UserModel
from .views.account import EmailValidationView, UserLoginView, UserLogoutView, ResetPasswordView
from .views.block_user import BlockUserView
from .views.changes import ChangesView
from .views.document import DocumentView
from .views import documents as documents_view
from .views import healthcheck as healthcheck_view

from .views.hide_version import HideVersionView
from .views.log import LogsView
from .views.protect_document import ProtectDocumentView
from .views.user import UsersView, UserView

log = logging.getLogger(__name__)


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

        self.add_module(healthcheck_view)

        self.add_resource(UsersView, "/users")
        self.add_resource(UserView, "/user/<int:id>")

        self.add_resource(UserLoginView, "/login")
        self.add_resource(UserLogoutView, "/logout")

        self.add_resource(EmailValidationView, "/validate_email")
        self.add_resource(ResetPasswordView, "/reset_password")

        self.add_module(documents_view)
        self.add_resource(DocumentView, "/document/<int:id>")

        self.add_resource(ChangesView, "/changes")
        self.add_resource(LogsView, "/logs")

        self.add_resource(ProtectDocumentView, "/protect_document/<int:id>")
        self.add_resource(BlockUserView, "/block_user/<int:id>")
        self.add_resource(HideVersionView, "/hide_version/<int:id>")

    def add_resource(self, *args, **kwargs):
        self._api.add_resource(*args, **kwargs)

    def add_module(self, module):

        for method in ["get", "post", "put", "delete"]:
            if hasattr(module, method):
                function = getattr(module, method)

                self._add_function(module.rule, function, method, endpoint=f"{method}_{module.__name__}")

    def _add_function(self, rule, function, method, endpoint):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Forbidden as e:
                return {"message": e.description}, 403
            except BadRequest as e:
                return {"message": e.description}, 400
            except Exception as e:  # pylint: disable=broad-except
                log.exception(e)
                return {"message": str(e)}, 500

        self.add_url_rule(rule, view_func=wrapper, methods=[method.upper()], endpoint=endpoint)

    def create_all(self):
        database.create_all()
