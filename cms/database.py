import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


def add_handler(handler):
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s"))
    handler.setLevel(logging.INFO)

    _logger = logging.getLogger("sqlalchemy")
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


def create_all():
    BaseModel.metadata.drop_all(bind=_engine)
    BaseModel.metadata.create_all(bind=_engine)


def execute(sql):
    return _engine.execute(sql)


add_handler(logging.NullHandler())

_engine = create_engine("sqlite://")
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=_engine))
BaseModel = declarative_base()
BaseModel.query = session.query_property()
