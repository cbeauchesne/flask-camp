from datetime import datetime, timedelta
import secrets

from flask_login import current_user
from sqlalchemy import Column, String, Text, Boolean, DateTime
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.security import generate_password_hash, check_password_hash

from cms.models import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    name = Column(String(64), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    _email = Column("email", String(120), index=True, unique=True)

    email_to_validate = Column(String(120))
    # linked with email_to_validate, if it's provided, email is validated
    email_token = Column(String(32))

    # unique usage token used to login without a password.
    # Useful for user creation and password reset
    _login_token = Column("login_token", String(32))
    _login_token_expiration_date = Column(DateTime)  # TODO

    ui_preferences = Column(Text)

    _roles = Column("roles", Text, default="", nullable=False)

    blocked = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

    @property
    def email(self):

        # last security fence, it should never happen
        if not current_user.is_authenticated:
            raise Forbidden()  # pragma: no cover

        if current_user.id != self.id and not current_user.is_admin and not current_user.is_moderator:
            raise Forbidden()  # pragma: no cover

        return self._email

    @property
    def email_is_validated(self):
        # At login, user is anonymous. But we must know if it's validated

        return self._email is not None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return password is not None and check_password_hash(self.password_hash, password)

    def check_login_token(self, login_token):  # TODO replace with login_with_token
        if self._login_token is None or login_token is None:
            return False

        if datetime.now() > self._login_token_expiration_date:
            return False

        if self._login_token != login_token:
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

        self.email_to_validate = email
        self.email_token = secrets.token_hex(self.__class__.password_hash.type.length)

        print(f"Update {self}'s email")
        # TODO send an email

    def validate_email(self):
        self.email_token = None
        self._email = self.email_to_validate
        self.email_to_validate = None

    def set_login_token(self):
        self._login_token = secrets.token_hex(self.__class__.password_hash.type.length)
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
