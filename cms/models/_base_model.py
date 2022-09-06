from sqlalchemy import Column, Integer

from sqlalchemy.orm import Query

from cms import database


class BaseModel(database.BaseModel):
    __abstract__ = True  # tells SQLAlchemy that this model should not be created in the database

    id = Column(Integer, primary_key=True, index=True)

    def create(self):
        if self.id is not None:
            raise ValueError(f"{self} should not have an ID")  # pragma: no cover

        database.session.add(self)  # pylint: disable=no-member
        database.session.commit()  # pylint: disable=no-member

    def update(self):
        database.session.add(self)  # pylint: disable=no-member
        database.session.commit()  # pylint: disable=no-member

    @classmethod
    def query(cls):
        return Query(cls, session=database.session)

    @classmethod
    def get(cls, **kwargs):
        return cls.query().filter_by(**kwargs).first()
