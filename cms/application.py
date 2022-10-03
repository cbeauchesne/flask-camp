import copy
import json
import logging
import sys
import warnings

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail, Message
from werkzeug.exceptions import HTTPException, NotFound

from . import config
from .limiter import limiter
from .models.document import Document
from .models.user import User as UserModel, AnonymousUser
from .services.database import database
from .services.memory_cache import MemoryCache
from .utils import GetDocument

from .views.account import user_login as user_login_view
from .views.account import email_validation as email_validation_view
from .views.account import reset_password as reset_password_view
from .views.account import roles as roles_view
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
            self.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://cms_user:cms_user@localhost:5432/cms"

        if "RATELIMIT_CONFIGURATION_FILE" in self.config:
            with open(self.config["RATELIMIT_CONFIGURATION_FILE"], mode="r", encoding="utf-8") as f:
                self._rate_limits = json.load(f)
        else:
            self._rate_limits = {}  # pragma: no cover

        ###############################################################################################################
        # init services

        self._init_memory_cache()

        self.database = database
        database.init_app(self)

        self._login_manager = LoginManager(self)
        self._login_manager.anonymous_user = AnonymousUser

        self.mail = Mail(self)

        limiter.init_app(self)

        self._cooker = None

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

        if self.config.get("INIT_DATABASES", None) == "True":
            self.add_url_rule("/init_databases", view_func=self.init_databases, methods=["GET"])

        if self.config.get("ERRORS_LOG_FILE", ""):
            self.logger.warning("Log errors to %s", self.config["ERRORS_LOG_FILE"])
            handler = logging.FileHandler(self.config["ERRORS_LOG_FILE"])
            handler.setLevel(logging.ERROR)
            self.logger.addHandler(handler)

    def _init_url_rules(self):
        # basic page: home and healtcheck
        self.add_modules(home_view, healthcheck_view)

        # access to users
        self.add_modules(users_view, user_view, current_user_view)

        # related to user account
        self.add_modules(user_login_view, email_validation_view, reset_password_view)

        # related to document
        self.add_modules(documents_view, document_view)
        self.add_modules(versions_view, version_view)
        self.add_modules(user_tags_view)

        # logs
        self.add_modules(logs_view)

        # reserved for moderators
        self.add_modules(protect_document_view)
        self.add_modules(block_user_view)
        self.add_modules(merge_view)

        # and reserved for admins
        self.add_modules(roles_view)

    def _init_memory_cache(self):
        redis_host = self.config.get("REDIS_HOST", "localhost")
        redis_port = self.config.get("REDIS_PORT", 6379)

        self.config["RATELIMIT_STORAGE_URI"] = f"redis://{redis_host}:{redis_port}"

        self.memory_cache = MemoryCache(host=redis_host, port=redis_port)

    def add_modules(self, *modules):

        for module in modules:
            for method in ["get", "post", "put", "delete"]:
                if hasattr(module, method):
                    function = getattr(module, method)
                    method = method.upper()

                    if module.rule in self._rate_limits and method in self._rate_limits[module.rule]:
                        limit = self._rate_limits[module.rule][method]
                        if limit is not None:
                            function = limiter.limit(limit)(function)
                            self.logger.info("Use %s rate limit for %s %s", limit, method, module.rule)
                        else:
                            function = limiter.exempt(function)

                    self.add_url_rule(
                        module.rule,
                        view_func=function,
                        methods=[method],
                        endpoint=f"{method}_{module.__name__}",
                    )

    def init_databases(self):
        """Will init database with an admin user"""

        self.logger.info("Init database")
        self.database.create_all()

        user = UserModel(name="admin", roles=["admin"])
        user.set_password("password")
        user.set_email("admin@example.com")
        user.validate_email(user._email_token)
        self.database.session.add(user)
        self.database.session.commit()

        return {"status": "ok"}

    def send_account_creation_mail(self, email, token, user):
        self.logger.info("Send registration mail to user %s", user.name)
        message = Message(
            "Welcome to example.com",  # TODO
            recipients=[email],
            body=f"https://example.com?email_token={token}",
            html=f'<a href="https://example.com?email_token={token}">click</a>',
        )

        self.mail.send(message)

    def send_email_change_mail(self, email, token, user):
        self.logger.info("Send mail address update mail to user %s", user.name)
        message = Message(
            "Change email",  # TODO
            recipients=[email],
            body=f"https://example.com?email_token={token}",
            html=f'<a href="https://example.com?email_token={token}">click</a>',
        )

        self.mail.send(message)

    def send_login_token_mail(self, email, token, user):
        self.logger.info("Send login token mail to user %s", user.name)
        message = Message(
            "Login token email",  # TODO
            recipients=[email],
            body=f"https://example.com?login_token={token}",
            html=f'<a href="https://example.com?login_token={token}">click</a>',
        )

        self.mail.send(message)

    def get_document(self, document_id):
        """This very simple function get a document id and returns it as a dict.
        It's only puprose it to hide the memcache complexity"""
        document_as_dict = self.memory_cache.get_document(document_id)

        if document_as_dict is None:  # document is not known by mem cache
            document = Document.get(id=document_id)

            if document is None:
                raise NotFound()

            document_as_dict = document.as_dict()

        return document_as_dict

    def get_cooked_document(self, document_id):
        """This very simple function get a document id and returns it as a dict.
        It's only puprose it to hide the memcache complexity"""
        cooked_document_as_dict = self.memory_cache.get_cooked_document(document_id)

        if cooked_document_as_dict is None:  # document is not known by mem cache
            document = Document.get(id=document_id)

            if document is None:
                raise NotFound()

            document_as_dict = document.as_dict()
            cooked_document_as_dict = self.cook(document_as_dict, save_in_memory_cache=True)

        return cooked_document_as_dict

    def get_associated_ids(self, document_as_dict):
        associated_ids = []

        if self._cooker is not None:
            get_document = GetDocument(self.get_document)
            self._cooker(copy.deepcopy(document_as_dict), get_document)
            associated_ids = list(get_document.loaded_document_ids)

        return associated_ids

    def cook(self, document_as_dict, save_in_memory_cache=False):
        result = copy.deepcopy(document_as_dict)

        if self._cooker is not None:
            self._cooker(result, GetDocument(self.get_document))

        if save_in_memory_cache:
            self.memory_cache.set_document(document_as_dict["id"], document_as_dict, result)

        return result

    def cooker(self, cooker):
        self.logger.info("Register cooker: %s", str(cooker))

        if not callable(cooker):
            raise TypeError("Your cooker is not callable")

        self._cooker = cooker

        return cooker
