from sqlalchemy import Column, Integer

from sqlalchemy.orm import Query

from cms import database


class BaseModel(database.BaseModel):
    __abstract__ = True  # tells SQLAlchemy that this model should not be created in the database

    id = Column(Integer, primary_key=True, index=True)

    def create(self):
        if self.id is not None:
            raise ValueError(f"{self} should not have an ID")

        database.session.add(self)  # pylint: disable=no-member
        database.session.commit()  # pylint: disable=no-member

        assert self.id is not None

    def update(self):
        database.session.add(self)  # pylint: disable=no-member
        database.session.commit()  # pylint: disable=no-member

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.get_dict_columns()}

    def get_dict_columns(self):
        return self.__table__.columns

    @classmethod
    def query(cls):
        return Query(cls, session=database.session)

    @classmethod
    def get(cls, **kwargs):
        return cls.query().filter_by(**kwargs).first()
