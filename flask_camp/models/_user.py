from datetime import datetime, timedelta
import json
import secrets

from flask import current_app
from flask_login import current_user
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import reconstructor
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized
from werkzeug.security import generate_password_hash, check_password_hash

from flask_camp.models._base_model import BaseModel
from flask_camp._utils import current_api


class AnonymousUser:  # pylint: disable=too-few-public-methods
    id = None

    blocked = False
    is_anonymous = True
    is_authenticated = False
    is_admin = False
    is_moderator = False

    @property
    def roles(self):
        return ["anonymous"]

    # useless ?
    # def get_id(self):
    #     return None


class User(BaseModel):  # pylint: disable=too-many-instance-attributes
    __tablename__ = "user_account"  # as user is a reserved word in postgres, we name it user_account

    name = Column(String(64), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    _email = Column("email", String(120), index=True, unique=True)

    _email_to_validate = Column("email_to_validate", String(120))
    # linked with email_to_validate, if it's provided, email is validated
    _email_token = Column("email_token", String(64))

    # unique usage token used to login without a password.
    # Useful for user creation and password reset
    _login_token = Column("login_token", String(64))
    _login_token_expiration_date = Column("login_token_expiration_date", DateTime)

    _ui_preferences = Column("ui_preferences", String, default="{}", nullable=False)

    roles = Column(ARRAY(String(16)), index=True, default=[])

    blocked = Column(Boolean, default=False, nullable=False)

    def __init__(self, ui_preferences=None, **kwargs):
        ui_preferences = {} if ui_preferences is None else ui_preferences
        super().__init__(_ui_preferences=json.dumps(ui_preferences), **kwargs)
        self._init_from_database()

    @reconstructor
    def _init_from_database(self):
        self._raw_ui_preferences = json.loads(self._ui_preferences)

    @property
    def ui_preferences(self):
        return self._raw_ui_preferences

    @ui_preferences.setter
    def ui_preferences(self, value):
        self._raw_ui_preferences = value
        self._ui_preferences = json.dumps(value)

    def __repr__(self):
        return f"<User {self.name}>"

    def _get_private_property(self, property_name):
        # last security fence, it should never happen

        if current_user.id != self.id and not current_user.is_admin and not current_user.is_moderator:
            current_app.logger.error("Unexpected access to user.%s", property_name)
            raise Forbidden()

        return getattr(self, property_name)

    @property
    def email(self):
        return self._get_private_property("_email")

    @property
    def email_is_validated(self):
        # At login, user is anonymous. But we must know if it's validated

        return self._email is not None

    def set_password(self, password):
        current_app.logger.info("Set %s's password", self)
        self.password_hash = generate_password_hash(password)
        self._login_token = None  # disable any login token

    def check_auth(self, password=None, token=None):
        if password is not None:
            return self._check_password(password)

        if token is not None:
            return self._check_login_token(token)

        return False

    def _check_password(self, password):
        if not check_password_hash(self.password_hash, password):
            current_app.logger.info("Check password failed for %s", self)
            return False

        return True

    def _check_login_token(self, login_token):
        if self._login_token is None or login_token is None:
            return False

        if datetime.now() > self._login_token_expiration_date:
            current_app.logger.info("Login token is expired for %s", self)
            return False

        if self._login_token != login_token:
            current_app.logger.error("Login token check fails for %s", self)
            return False

        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self._email is not None

    def get_id(self):
        return str(self.id)

    def as_dict(self, include_personal_data=False):
        result = {
            "id": self.id,
            "name": self.name,
            "roles": self.roles,
            "blocked": self.blocked,
            "ui_preferences": self.ui_preferences,
        }

        if include_personal_data:
            result["email"] = self.email

        return result

    def set_email(self, email):
        if User.get(_email=email) is not None:
            raise BadRequest("A user still exists with this email")

        self._email_to_validate = email
        # each byte is converted to two hex digit, so we need len/2
        self._email_token = secrets.token_hex(int(self.__class__._email_token.type.length / 2))

        current_app.logger.info("Update %s's email", self)

    def send_account_creation_mail(self):
        current_api.mail.send_account_creation(self._email_to_validate, self._email_token, self)

    def send_email_change_mail(self):
        current_api.mail.send_email_change(self._email_to_validate, self._email_token, self)

    def send_login_token_mail(self):
        current_api.mail.send_login_token(self._email, self._login_token, self)

    def validate_email(self, token):

        if self._email_token is None:
            raise BadRequest("There is no email to validate")

        if token != self._email_token:
            raise Unauthorized("Token doesn't match")

        self._email_token = None
        self._email = self._email_to_validate
        self._email_to_validate = None

    def set_login_token(self):
        # each byte is converted to two hex digit, so we need len/2
        self._login_token = secrets.token_hex(int(self.__class__._login_token.type.length / 2))
        self._login_token_expiration_date = datetime.now() + timedelta(hours=1)

    @property
    def is_admin(self):
        return "admin" in self.roles

    @property
    def is_moderator(self):
        return "moderator" in self.roles

    @property
    def login_token_expiration_date(self):
        return self._login_token_expiration_date
