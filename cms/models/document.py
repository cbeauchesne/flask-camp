from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy import String

from sqlalchemy.orm import relationship

from cms.models import BaseModel


class Document(BaseModel):
    __tablename__ = "document"

    namespace = Column(String, index=True)


class DocumentVersion(BaseModel):
    __tablename__ = "document_version"

    document_id = Column(Integer, ForeignKey("document.id"), index=True)

    author_id = Column(Integer, ForeignKey("user.id"), index=True)
    timestamp = Column(DateTime)
    comment = Column(String)

    data = Column(String)

    def __init__(self, **kwargs):
        kwargs["timestamp"] = datetime.now()
        super().__init__(**kwargs)

    def as_dict(self):
        return {
            "id": self.document_id,
            "version_id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "comment": self.comment,
            "data": self.data,
            "author_id": self.author_id,
        }
