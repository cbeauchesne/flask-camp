from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class Database:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def create_all(self, metadata):
        metadata.create_all(bind=self.engine)

    def execute(self, sql):
        return self.engine.execute(sql)
