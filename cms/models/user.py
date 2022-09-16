from datetime import datetime, timedelta
import logging
import secrets

from flask import current_app
from flask_login import current_user
from sqlalchemy import Column, String, Text, Boolean, DateTime
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized
from werkzeug.security import generate_password_hash, check_password_hash

from cms.models import BaseModel

log = logging.getLogger(__name__)


class User(BaseModel):
    __tablename__ = "user"

    name = Column(String(64), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    _email = Column("email", String(120), index=True, unique=True)

    _email_to_validate = Column("email_to_validate", String(120))
    # linked with email_to_validate, if it's provided, email is validated
    _email_token = Column("email_token", String(64))

    # unique usage token used to login without a password.
    # Useful for user creation and password reset
    _login_token = Column("login_token", String(64))
    _login_token_expiration_date = Column("login_token_expiration_date", DateTime)  # TODO

    ui_preferences = Column(Text)

    _roles = Column("roles", Text, default="", nullable=False)

    blocked = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

    def _get_private_property(self, property_name):
        # last security fence, it should never happen
        if not current_user.is_authenticated:
            log.error("Unexpected access to user.%s", property_name)
            raise Forbidden()

        if current_user.id != self.id and not current_user.is_admin and not current_user.is_moderator:
            log.error("Unexpected access to user.%s", property_name)
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
        log.info("Set %s's password", self)
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if password is None:
            return False
        if not check_password_hash(self.password_hash, password):
            log.info("Check password failed for %s", self)
            return False

        return True

    def check_login_token(self, login_token):  # TODO replace with login_with_token
        if self._login_token is None or login_token is None:
            return False

        if datetime.now() > self._login_token_expiration_date:
            log.info("Login token is expired for %s", self)
            return False

        if self._login_token != login_token:
            log.error("Login token check fails for %s", self)
            return False

        self._login_token = None

        return True

    @property
    def is_authenticated(self):
        return self.id is not None

    @property
    def is_active(self):
        return self.is_authenticated and self._email is not None

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

        log.info("Update %s's email", self)

    def send_account_creation_mail(self):
        current_app.send_account_creation_mail(self._email_to_validate, self._email_token, self)

    def send_email_change_mail(self):
        current_app.send_email_change_mail(self._email_to_validate, self._email_token, self)

    def send_login_token_mail(self):
        current_app.send_login_token_mail(self._email, self._login_token, self)

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
    def roles(self):
        return [] if not self._roles else self._roles.split(",")

    @roles.setter
    def roles(self, value):
        self._roles = ",".join(value)

    @property
    def login_token_expiration_date(self):
        return self._login_token_expiration_date
