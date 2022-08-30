from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from cms.models import BaseModel


class Profile(BaseModel):
    __tablename__ = "profile"
