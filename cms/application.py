import logging
import sys
import warnings

from fakeredis import FakeRedis
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail, Message
from redis import Redis as RedisClient
from werkzeug.exceptions import HTTPException


from . import config
from .limiter import limiter
from .models.user import User as UserModel, AnonymousUser
from .services.database import database
from .services.memory_cache import MemoryCache

from .views.account import user_login as user_login_view
from .views.account import email_validation as email_validation_view
from .views.account import reset_password as reset_password_view
from .views import block_user as block_user_view
from .views import current_user as current_user_view
from .views import document as document_view
from .views import documents as documents_view
from .views import healthcheck as healthcheck_view
from .views import home as home_view
from .views import logs as logs_view
from .views import merge as merge_view
from .views import protect_document as protect_document_view
from .views import user as user_view
from .views import users as users_view
from .views import user_tags as user_tags_view
from .views import versions as versions_view
from .views import version as version_view


logging.basicConfig(format="%(asctime)s [%(levelname)8s] %(message)s")
log = logging.getLogger(__name__)


class Application(Flask):
    def __init__(self, config_object=None):
        super().__init__(__name__, static_folder=None)

        if config_object:
            self.config.from_object(config_object)
        elif self.debug:  # pragma: no cover
            self.config.from_object(config.Development)
        else:  # pragma: no cover
            self.config.from_object(config.Production)

        self.config.from_prefixed_env()

        if self.config.get("SECRET_KEY", None) is None:  # pragma: no cover
            warnings.warn("Please set FLASK_SECRET_KEY environment variable")
            sys.exit(1)

        if self.config.get("MAIL_DEFAULT_SENDER", None) is None:
            if not self.testing:
                warnings.warn(
                    "FLASK_MAIL_DEFAULT_SENDER environment variable is not set, defaulting to do-not-reply@example.com"
                )
            self.config["MAIL_DEFAULT_SENDER"] = "do-not-reply@example.com"

        if self.config.get("SQLALCHEMY_DATABASE_URI", None) is None:
            if not self.testing:
                warnings.warn("FLASK_SQLALCHEMY_DATABASE_URI environment variable is not set, defaulting to memory")
            self.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

        ###############################################################################################################
        # init services

        self._init_memory_cache()

        self.database = database
        database.init_app(self)

        self._login_manager = LoginManager(self)
        self._login_manager.anonymous_user = AnonymousUser

        self.mail = Mail(self)

        limiter.init_app(self)

        @self._login_manager.user_loader  # pylint: disable=no-member
        def load_user(user_id):
            return UserModel.get(id=int(user_id))

        @self.teardown_appcontext
        def shutdownsession(exception=None):  # pylint: disable=unused-argument
            self.database.session.remove()

        @self.errorhandler(HTTPException)
        def rest_error_handler(e):
            result = {"status": "error", "name": e.name, "description": e.description}
            if hasattr(e, "data"):
                result["data"] = e.data
            return result, e.code

        self._init_url_rules()

        if self.config.get("INIT_DATABASE", None) == "True":
            self.add_url_rule("/init_database", view_func=self.init_database, methods=["GET"])

        if self.config.get("ERRORS_LOG_FILE", ""):
            self.logger.warning("Log errors to %s", self.config["ERRORS_LOG_FILE"])
            handler = logging.FileHandler(self.config["ERRORS_LOG_FILE"])
            handler.setLevel(logging.ERROR)
            self.logger.addHandler(handler)

    def _init_url_rules(self):
        self.add_module(home_view)

        self.add_module(healthcheck_view)

        self.add_module(users_view)
        self.add_module(user_view)
        self.add_module(current_user_view)

        self.add_module(user_login_view)
        self.add_module(email_validation_view)
        self.add_module(reset_password_view)

        self.add_module(documents_view)
        self.add_module(document_view)
        self.add_module(versions_view)
        self.add_module(version_view)

        self.add_module(user_tags_view)

        self.add_module(logs_view)

        self.add_module(protect_document_view)
        self.add_module(block_user_view)
        self.add_module(merge_view)

    def _init_memory_cache(self):
        redis_host = self.config.get("REDIS_HOST", None)
        redis_port = self.config.get("REDIS_PORT", 6379)

        if redis_host is None:
            if not self.testing and not self.debug:
                warnings.warn("FLASK_REDIS_HOST environment variable is not set, defaulting to fake-redis-client")
            self.config["RATELIMIT_STORAGE_URI"] = "memory://"
            memory_cache_instance = FakeRedis()
        else:  # pragma: no cover
            self.config["RATELIMIT_STORAGE_URI"] = f"redis://{redis_host}:{redis_port}"
            memory_cache_instance = RedisClient(host=redis_host, port=redis_port)

        self.memory_cache = MemoryCache(client=memory_cache_instance)

    def add_module(self, module):

        for method in ["get", "post", "put", "delete"]:
            if hasattr(module, method):
                function = getattr(module, method)

                self.add_url_rule(
                    module.rule, view_func=function, methods=[method.upper()], endpoint=f"{method}_{module.__name__}"
                )

    def init_database(self):
        """Will init database with an admin user"""

        log.info("Init database")
        self.database.create_all()

        user = UserModel(name="admin", roles=["admin"])
        user.set_password("password")
        user.set_email("admin@example.com")
        user.validate_email(user._email_token)

        self.database.session.add(user)
        self.database.session.commit()

        return {"status": "ok"}

    def create_all(self):
        self.database.create_all()

    def send_account_creation_mail(self, email, token, user):
        log.info("Send registration mail to user %s", user.name)
        message = Message(
            "Welcome to example.com",  # TODO
            recipients=[email],
            body=f"https://example.com?email_token={token}",
            html=f'<a href="https://example.com?email_token={token}">click</a>',
        )

        self.mail.send(message)

    def send_email_change_mail(self, email, token, user):
        log.info("Send mail address update mail to user %s", user.name)
        message = Message(
            "Change email",  # TODO
            recipients=[email],
            body=f"https://example.com?email_token={token}",
            html=f'<a href="https://example.com?email_token={token}">click</a>',
        )

        self.mail.send(message)

    def send_login_token_mail(self, email, token, user):
        log.info("Send login token mail to user %s", user.name)
        message = Message(
            "Login token email",  # TODO
            recipients=[email],
            body=f"https://example.com?login_token={token}",
            html=f'<a href="https://example.com?login_token={token}">click</a>',
        )

        self.mail.send(message)
