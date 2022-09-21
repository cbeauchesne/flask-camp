from sqlalchemy import Column, Integer
from cms.services.database import database


class BaseModel(database.Model):  # pylint: disable=too-few-public-methods
    __abstract__ = True  # tells SQLAlchemy that this model should not be created in the database

    id = Column(Integer, primary_key=True, index=True)

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()
