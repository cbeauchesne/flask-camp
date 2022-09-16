from flask import current_app
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Query, declarative_base


class BaseModel(declarative_base()):
    __abstract__ = True  # tells SQLAlchemy that this model should not be created in the database

    id = Column(Integer, primary_key=True, index=True)

    def create(self):
        if self.id is not None:
            raise ValueError(f"{self} should not have an ID")  # pragma: no cover

        current_app.database.session.add(self)  # pylint: disable=no-member
        current_app.database.session.commit()  # pylint: disable=no-member

    def update(self):
        current_app.database.session.add(self)  # pylint: disable=no-member
        current_app.database.session.commit()  # pylint: disable=no-member

    @classmethod
    def query(cls):
        return Query(cls, session=current_app.database.session)

    @classmethod
    def get(cls, **kwargs):
        return cls.query().filter_by(**kwargs).first()
