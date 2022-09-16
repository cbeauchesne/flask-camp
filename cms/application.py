import logging
import secrets

from flask import Flask
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException

from . import config
from .database import Database
from .limiter import limiter
from .models.user import User as UserModel
from .models import BaseModel

from .views.account import user_login as user_login_view
from .views.account import email_validation as email_validation_view
from .views.account import reset_password as reset_password_view
from .views import block_user as block_user_view
from .views import document_versions as document_versions_view
from .views import document_version as document_version_view
from .views import document as document_view
from .views import documents as documents_view
from .views import healthcheck as healthcheck_view
from .views import logs as logs_view
from .views import protect_document as protect_document_view
from .views import user as user_view
from .views import users as users_view
from .views import user_tags as user_tags_view


logging.basicConfig(format="%(asctime)s [%(levelname)8s] %(message)s")
log = logging.getLogger(__name__)


class Application(Flask):
    def __init__(self, config_object=None):
        super().__init__(__name__)

        if config_object:
            self.config.from_object(config_object)
        elif self.debug:  # pragma: no cover
            self.config.from_object(config.Development)
        else:  # pragma: no cover
            self.config.from_object(config.Production)

        self.config.from_prefixed_env()

        self.database = Database(database_uri=self.config["DATABASE_URI"])

        self._login_manager = LoginManager(self)
        self.secret_key = secrets.token_hex()

        limiter.init_app(self)

        @self.login_manager.user_loader  # pylint: disable=no-member
        def load_user(user_id):
            return UserModel.get(id=int(user_id))

        @self.teardown_appcontext
        def shutdownsession(exception=None):  # pylint: disable=unused-argument
            self.database.session.remove()

        @self.errorhandler(HTTPException)
        def rest_error_handler(e):
            return {"status": "error", "name": e.name, "description": e.description}, e.code

        self.add_module(healthcheck_view)

        self.add_module(users_view)
        self.add_module(user_view)

        self.add_module(user_login_view)

        self.add_module(email_validation_view)
        self.add_module(reset_password_view)

        self.add_module(documents_view)
        self.add_module(document_view)
        self.add_module(document_versions_view)

        self.add_module(logs_view)

        self.add_module(protect_document_view)
        self.add_module(block_user_view)

        self.add_module(user_tags_view)
        self.add_module(document_version_view)

    def add_module(self, module):

        for method in ["get", "post", "put", "delete"]:
            if hasattr(module, method):
                function = getattr(module, method)

                self.add_url_rule(
                    module.rule, view_func=function, methods=[method.upper()], endpoint=f"{method}_{module.__name__}"
                )

    def create_all(self):
        self.database.create_all(BaseModel.metadata)
