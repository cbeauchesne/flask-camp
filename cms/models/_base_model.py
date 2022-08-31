from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer

from sqlalchemy.orm import Query

from cms import database


class BaseModel(declarative_base()):
    __abstract__ = True  # tells SQLAlchemy that this model should not be created in the database

    id = Column(Integer, primary_key=True, index=True)

    def create(self):
        if self.id is not None:
            raise ValueError(f"{self} should not have an ID")

        # todo : context manager
        session = database.current_session
        session.add(self)
        session.commit()

        assert self.id is not None

    def update(self):
        session = database.current_session
        session.add(self)
        session.commit()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.get_dict_columns()}

    def get_dict_columns(self):
        return self.__table__.columns

    @classmethod
    def query(cls):
        return Query(cls, session=database.current_session)

    @classmethod
    def get(cls, **kwargs):
        return cls.query().filter_by(**kwargs).first()
