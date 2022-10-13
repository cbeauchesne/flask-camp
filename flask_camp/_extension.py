import copy
import json
from types import ModuleType
import warnings

from flask import request
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException, NotFound

from ._schemas import SchemaValidator
from ._services._database import database
from ._services._memory_cache import memory_cache
from ._services._security import check_rights, allow
from ._services._send_mail import SendMail
from ._utils import GetDocument
from .exceptions import ConfigurationError
from .models._document import Document
from .models._log import Log
from .models._user import User as UserModel, AnonymousUser


from .views.account import block_user as block_user_view
from .views.account import current_user as current_user_view
from .views.account import email_validation as email_validation_view
from .views.account import rename_user as rename_user_view
from .views.account import reset_password as reset_password_view
from .views.account import roles as roles_view
from .views.account import user as user_view
from .views.account import user_login as user_login_view
from .views.account import users as users_view
from .views.content import document as document_view
from .views.content import documents as documents_view
from .views.content import version as version_view
from .views.content import versions as versions_view
from .views.content import merge as merge_view
from .views.content import protect_document as protect_document_view
from .views.content import user_tags as user_tags_view
from .views import healthcheck as healthcheck_view
from .views import home as home_view
from .views import logs as logs_view


# pylint: disable=too-many-instance-attributes
class RestApi:
    def __init__(  # pylint: disable=too-many-locals
        self,
        app=None,
        cooker=None,
        schemas_directory=None,
        document_schemas=None,
        user_roles="",
        rate_limit_cost_function=None,
        rate_limits_file=None,
        user_can_delete=False,
        before_user_creation=None,
        before_document_save=None,
        before_document_delete=None,
        update_search_query=None,
        url_prefix="",
    ):
        self.database = database
        self.limiter = Limiter(key_func=get_remote_address)
        self.memory_cache = memory_cache
        self.mail = SendMail()

        self._rate_limit_cost_function = rate_limit_cost_function

        self.user_can_delete = user_can_delete

        self.before_user_creation = self._hook_function(before_user_creation)
        self.before_document_save = self._hook_function(before_document_save)
        self.before_document_delete = self._hook_function(before_document_delete)
        self.update_search_query = update_search_query if update_search_query is not None else lambda query: query

        if rate_limits_file:
            with open(rate_limits_file, mode="r", encoding="utf-8") as f:
                self._rate_limits = json.load(f)
        else:
            self._rate_limits = {}

        self._user_roles = {"admin", "moderator"} | self._parse_user_roles(user_roles)
        self._cooker = cooker

        if schemas_directory:
            self._schema_validator = SchemaValidator(schemas_directory)
        else:
            self._schema_validator = None

        self._document_schemas = document_schemas
        self._url_prefix = url_prefix

        self.allow = allow

        if app is not None:
            self.init_app(app)
        else:
            self._configuration_checks()

    def init_app(self, app):
        app.extensions["flask-camp"] = self

        self._init_config(app)
        self._init_database(app)
        self.memory_cache.init_app(app)
        self.mail.init_app(app)
        self._init_login_manager(app)
        self._init_error_handler(app)
        self._init_rate_limiter(app)
        self._init_url_rules(app)

        self._configuration_checks()

        if app.debug:  # pragma: no cover
            with app.app_context():
                self.database.create_all()

    def _configuration_checks(self):
        # post configuration checks
        if self._cooker is not None and not callable(self._cooker):
            raise ConfigurationError(f"cooker is not callable: {self._cooker}")

        if self._schema_validator and self._document_schemas:
            for filename in self._document_schemas:
                if not self._schema_validator.exists(filename):
                    raise FileNotFoundError(f"Schema {filename} does not exists")

        for role in ("anonymous", "authenticated"):
            if role in self._user_roles:
                raise ConfigurationError(f"{role} can't be a user role")

        self._check_url_prefix(self._url_prefix)

    @staticmethod
    def _parse_user_roles(user_roles):
        if isinstance(user_roles, str):  # allow comma separated string
            user_roles = user_roles.split(",")

        return set(role.lower().strip() for role in user_roles if len(role.strip()) != 0)

    @staticmethod
    def _hook_function(function):

        if function is not None and not callable(function):
            raise ConfigurationError(f"Hook object is not callable: {function}")

        return function if function else lambda *args, **kwargs: ...

    def _init_config(self, app):
        if app.config.get("MAIL_DEFAULT_SENDER", None) is None:
            if not app.testing and not app.debug:
                warnings.warn("MAIL_DEFAULT_SENDER is not set, defaulting to do-not-reply@example.com")
            app.config["MAIL_DEFAULT_SENDER"] = "do-not-reply@example.com"

    def _init_database(self, app):

        if app.config.get("SQLALCHEMY_DATABASE_URI", None) is None:
            default = "postgresql://flask_camp_user:flask_camp_user@localhost:5432/flask_camp"
            app.config["SQLALCHEMY_DATABASE_URI"] = default

            if not app.testing and not app.debug:
                warnings.warn(f"SQLALCHEMY_DATABASE_URI is not set, defaulting to {default}")

        self.database.init_app(app)

        @app.teardown_appcontext
        def shutdown_session(exception=None):  # pylint: disable=unused-argument
            self.database.session.remove()

    def _init_login_manager(self, app):
        login_manager = LoginManager(app)
        login_manager.anonymous_user = AnonymousUser

        @login_manager.user_loader  # pylint: disable=no-member
        def load_user(user_id):
            return UserModel.get(id=int(user_id))

    def _init_error_handler(self, app):
        @app.errorhandler(HTTPException)
        def rest_error_handler(e):
            result = {"status": "error", "name": e.name, "description": e.description}
            if hasattr(e, "data"):
                result["data"] = e.data
            return result, e.code

    def _init_rate_limiter(self, app):

        if "RATELIMIT_STORAGE_URI" not in app.config:
            redis_host = app.config.get("REDIS_HOST", "localhost")
            redis_port = app.config.get("REDIS_PORT", 6379)
            app.config["RATELIMIT_STORAGE_URI"] = f"redis://{redis_host}:{redis_port}"

        self.limiter.init_app(app)

    def _init_url_rules(self, app):
        # basic page: home and healtcheck
        self.add_modules(app, home_view, healthcheck_view)

        # access to users
        self.add_modules(app, users_view, user_view, current_user_view)

        # related to user account
        self.add_modules(app, user_login_view, email_validation_view, reset_password_view)

        # related to document
        self.add_modules(app, documents_view, document_view)
        self.add_modules(app, versions_view, version_view)
        self.add_modules(app, user_tags_view)

        # logs
        self.add_modules(app, logs_view)

        # reserved for moderators
        self.add_modules(app, protect_document_view)
        self.add_modules(app, block_user_view, rename_user_view)
        self.add_modules(app, merge_view)

        # reserved for admins
        self.add_modules(app, roles_view)

    @property
    def user_roles(self):
        return set(self._user_roles)

    ### Public methods

    def get_associated_ids(self, document_as_dict):
        associated_ids = []

        if self._cooker is not None:
            get_document = GetDocument(self.get_document)
            self._cooker(copy.deepcopy(document_as_dict), get_document)
            associated_ids = list(get_document.loaded_document_ids)

        return associated_ids

    def get_document(self, document_id):
        """This very simple function get a document id and returns it as a dict.
        It's only puprose it to hide the memcache complexity"""
        document_as_dict = memory_cache.get_document(document_id)

        if document_as_dict is None:  # document is not known by mem cache
            document = Document.get(id=document_id)

            if document is None:
                raise NotFound()

            document_as_dict = document.as_dict()

        return document_as_dict

    def get_cooked_document(self, document_id):
        """This very simple function get a document id and returns it as a dict.
        It's only puprose it to hide the memcache complexity"""
        cooked_document_as_dict = memory_cache.get_cooked_document(document_id)

        if cooked_document_as_dict is None:  # document is not known by mem cache
            document = Document.get(id=document_id)

            if document is None:
                raise NotFound()

            document_as_dict = document.as_dict()
            if document.is_redirection:
                cooked_document_as_dict = document_as_dict
            else:
                cooked_document_as_dict = self.cook(document_as_dict, save_in_memory_cache=True)

        return cooked_document_as_dict

    def cook(self, document_as_dict, save_in_memory_cache=False):
        result = copy.deepcopy(document_as_dict)

        if self._cooker is not None:
            self._cooker(result, GetDocument(self.get_document))

        if save_in_memory_cache:
            memory_cache.set_document(document_as_dict["id"], document_as_dict, result)

        return result

    def validate_user_schemas(self, data):
        if self._schema_validator is not None:
            self._schema_validator.validate(data, *self._document_schemas)

    def add_modules(self, app, *modules, url_prefix=None):
        possible_user_roles = self.user_roles | {"anonymous", "authenticated"}

        url_prefix = url_prefix if url_prefix is not None else self._url_prefix

        self._check_url_prefix(url_prefix)

        for module in modules:
            if not hasattr(module, "rule"):
                raise ConfigurationError(f"{module} does not have a rule attribute")

            for method in ["get", "post", "put", "delete"]:
                if hasattr(module, method):
                    function = getattr(module, method)
                    method = method.upper()

                    if not hasattr(function, "allowed_roles") or not hasattr(function, "allow_blocked"):
                        raise ConfigurationError(f"Please use @flask_camp.allow decorator on {function}")

                    for role in function.allowed_roles:
                        if role not in possible_user_roles:
                            raise ConfigurationError(f"{role} is not recognised")

                    function = check_rights(function)

                    rule = f"{url_prefix}{module.rule}"

                    if rule in self._rate_limits and method in self._rate_limits[rule]:
                        limit = self._rate_limits[rule][method]
                        if limit is not None:
                            function = self.limiter.limit(limit, cost=self._rate_limit_cost_function)(function)
                            app.logger.info("Use %s rate limit for %s %s", limit, method, rule)
                        else:
                            function = self.limiter.exempt(function)

                    if isinstance(module, ModuleType):
                        endpoint = f"{method}_{module.__name__}_{rule}"
                    else:
                        endpoint = f"{method}_{module.__class__.__name__}_{rule}"

                    app.add_url_rule(
                        rule,
                        view_func=function,
                        methods=[method],
                        endpoint=endpoint,
                    )

    def add_log(self, action, comment=None, target_user=None, document=None, merged_document=None, version=None):
        if comment is None:
            comment = request.get_json().get("comment", "")

        document_id = document.id if document is not None else None
        merged_document_id = merged_document.id if merged_document is not None else None
        version_id = version.id if version is not None else None

        log = Log(
            action=action,
            comment=comment,
            target_user=target_user,
            document_id=document_id,
            merged_document_id=merged_document_id,
            version_id=version_id,
        )
        self.database.session.add(log)

    @staticmethod
    def _check_url_prefix(url_prefix):

        if len(url_prefix) != 0 and not url_prefix.startswith("/"):
            raise ConfigurationError("url_prefix should starts with a `/`")

        if url_prefix.endswith("/"):
            raise ConfigurationError("url_prefix should not ends with a `/`")
