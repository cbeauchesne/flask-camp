import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


class FakeStream:
    def write(self, *args, **kwargs):
        pass


def add_logger(stream):
    _log_handler = logging.StreamHandler(stream)
    _log_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s"))
    _log_handler.setLevel(logging.INFO)

    _logger = logging.getLogger("sqlalchemy")
    _logger.addHandler(_log_handler)
    _logger.setLevel(logging.INFO)


def create_all():
    BaseModel.metadata.drop_all(bind=_engine)
    BaseModel.metadata.create_all(bind=_engine)


def execute(sql):
    return _engine.execute(sql)


add_logger(FakeStream())

_engine = create_engine("sqlite://")
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=_engine))
BaseModel = declarative_base()
BaseModel.query = session.query_property()
