from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from cms.models import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    username = Column(String(64), index=True, unique=True, nullable=False)
    email = Column(String(120), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    validation_token = Column(String(32))
    ui_preferences = Column(Text)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_dict_columns(cls):
        return (cls.id, cls.username, cls.email)

    @property
    def is_authenticated(self):
        return self.id is not None

    @property
    def is_active(self):
        return self.is_authenticated and self.validation_token is None

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    def get_id(self):
        return str(self.id)

    @classmethod
    def get_dict_columns(cls):
        return (cls.id, cls.username, cls.email, cls.ui_preferences)
