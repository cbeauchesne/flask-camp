import copy
import json
import logging
import sys
import warnings

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager

from werkzeug.exceptions import HTTPException, NotFound

from . import config
from .models.document import Document
from .models.user import User as UserModel, AnonymousUser
from .schemas import SchemaValidator
from .services.database import database
from .services.memory_cache import MemoryCache
from .services.send_mail import SendMail
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

    # pylint: disable=too-many-instance-attributes
    def __init__(self, config_object=None, rate_limit_cost_function=None):
        super().__init__(__name__, static_folder=None)

        self._init_config(config_object)

        ###############################################################################################################
        # init services

        self._init_memory_cache()

        self.database = database
        database.init_app(self)

        self.mail = SendMail(self)

        self._login_manager = LoginManager(self)
        self._login_manager.anonymous_user = AnonymousUser

        self.limiter = Limiter(app=self, key_func=get_remote_address)
        self._rate_limit_cost_function = rate_limit_cost_function

        self._cooker = None

        @self._login_manager.user_loader  # pylint: disable=no-member
        def load_user(user_id):
            return UserModel.get(id=int(user_id))

        @self.teardown_appcontext
        def shutdown_session(exception=None):  # pylint: disable=unused-argument
            self.database.session.remove()

        @self.errorhandler(HTTPException)
        def rest_error_handler(e):
            result = {"status": "error", "name": e.name, "description": e.description}
            if hasattr(e, "data"):
                result["data"] = e.data
            return result, e.code

        self._init_url_rules()

        if self.config.get("ERRORS_LOG_FILE", ""):
            self.logger.warning("Log errors to %s", self.config["ERRORS_LOG_FILE"])
            handler = logging.FileHandler(self.config["ERRORS_LOG_FILE"])
            handler.setLevel(logging.ERROR)
            self.logger.addHandler(handler)

        self._schema_validator = None
        self._schema_filenames = None

    def _init_config(self, config_object):

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
            self.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wiki_api_user:wiki_api_user@localhost:5432/wiki_api"

        if "RATELIMIT_CONFIGURATION_FILE" in self.config:
            with open(self.config["RATELIMIT_CONFIGURATION_FILE"], mode="r", encoding="utf-8") as f:
                self._rate_limits = json.load(f)
        else:
            self._rate_limits = {}  # pragma: no cover

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

        # reserved for admins
        self.add_modules(roles_view)

        # other routes
        if self.config.get("INIT_DATABASES", None) == "True":
            self.add_url_rule("/init_databases", view_func=self.init_databases, methods=["GET"])

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
                            function = self.limiter.limit(limit, cost=self._rate_limit_cost_function)(function)
                            self.logger.info("Use %s rate limit for %s %s", limit, method, module.rule)
                        else:
                            function = self.limiter.exempt(function)

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

    def validate_user_schemas(self, data):
        if self._schema_validator is not None:
            self._schema_validator.validate(data, *self._schema_filenames)

    ###########################################################################
    # public methods
    def register_cooker(self, cooker):
        self.logger.info("Register cooker: %s", str(cooker))

        if not callable(cooker):
            raise TypeError("Your cooker is not callable")

        self._cooker = cooker

    def register_schemas(self, base_dir, schema_filenames):
        self.logger.info("Register schemas: %s, %s", base_dir, str(schema_filenames))

        self._schema_validator = SchemaValidator(base_dir)
        self._schema_filenames = schema_filenames

        for filename in self._schema_filenames:
            if not self._schema_validator.exists(filename):
                raise FileNotFoundError(f"{filename} does not exists")


def create():
    return Application()
