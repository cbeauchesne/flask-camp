from flask import current_app
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base


class BaseModel(declarative_base()):
    __abstract__ = True  # tells SQLAlchemy that this model should not be created in the database

    id = Column(Integer, primary_key=True, index=True)

    @classmethod
    def query(cls):
        return current_app.database.session.query(cls)

    @classmethod
    def get(cls, **kwargs):
        return cls.query().filter_by(**kwargs).first()
