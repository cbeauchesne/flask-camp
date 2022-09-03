from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


_engine = create_engine("sqlite://", echo=True)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=_engine))
BaseModel = declarative_base()
BaseModel.query = session.query_property()


def create_all():
    BaseModel.metadata.drop_all(bind=_engine)
    BaseModel.metadata.create_all(bind=_engine)


def execute(sql):
    return _engine.execute(sql)
