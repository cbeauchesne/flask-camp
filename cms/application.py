from functools import wraps
import logging
import secrets

from flask import Flask
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException

from . import database
from .limiter import limiter
from .models.user import User as UserModel

from .views.account import user_login as user_login_view
from .views.account import email_validation as email_validation_view
from .views.account import reset_password as reset_password_view
from .views import block_user as block_user_view
from .views import changes as changes_view
from .views import document as document_view
from .views import documents as documents_view
from .views import healthcheck as healthcheck_view
from .views import hide_version as hide_version_view
from .views import logs as logs_view
from .views import protect_document as protect_document_view
from .views import user as user_view
from .views import users as users_view

logging.basicConfig(format="%(asctime)s [%(levelname)8s] %(message)s")
log = logging.getLogger(__name__)


class Application(Flask):
    def __init__(self, **kwargs):
        super().__init__(__name__)

        self.config.from_object(kwargs)

        self._login_manager = LoginManager(self)
        self.secret_key = secrets.token_hex()

        limiter.init_app(self)

        @self.login_manager.user_loader  # pylint: disable=no-member
        def load_user(user_id):
            return UserModel.get(id=int(user_id))

        @self.teardown_appcontext
        def shutdownsession(exception=None):  # pylint: disable=unused-argument
            database.session.remove()

        self.add_module(healthcheck_view)

        self.add_module(users_view)
        self.add_module(user_view)

        self.add_module(user_login_view)

        self.add_module(email_validation_view)
        self.add_module(reset_password_view)

        self.add_module(documents_view)
        self.add_module(document_view)

        self.add_module(changes_view)
        self.add_module(logs_view)

        self.add_module(protect_document_view)
        self.add_module(block_user_view)
        self.add_module(hide_version_view)

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
            except HTTPException as e:
                return {"status": "error", "name": e.name, "description": e.description}, e.code
            except Exception as e:  # pylint: disable=broad-except
                log.exception(e)
                return {"status": "error", "name": e.__class__.__name__, "description": str(e)}, 500

        self.add_url_rule(rule, view_func=wrapper, methods=[method.upper()], endpoint=endpoint)

    def create_all(self):
        database.create_all()
