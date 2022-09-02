from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class _DataBase:
    def __init__(self):
        self._connection = None
        self.current_session = None

    def connect(self, echo=False):
        self._connection = create_engine("sqlite://", echo=echo)

    def get_session(self, autocommit=False):
        return Session(self._connection, autocommit=autocommit)

    def execute(self, sql):
        return self._connection.execute(sql)


database = _DataBase()
