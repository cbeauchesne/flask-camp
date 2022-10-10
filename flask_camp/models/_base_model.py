from sqlalchemy import Column, Integer
from flask_camp._services._database import database


class BaseModel(database.Model):  # pylint: disable=too-few-public-methods
    __abstract__ = True  # tells SQLAlchemy that this model should not be created in the database

    id = Column(Integer, primary_key=True, index=True)

    @classmethod
    def get(cls, with_for_update=False, **kwargs):
        query = cls.query.filter_by(**kwargs)

        if with_for_update:
            query = query.with_for_update()

        return query.first()
