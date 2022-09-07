import json
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from cms.models import BaseModel


class Document(BaseModel):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String, index=True)

    protected = Column(Boolean, nullable=False, default=False)

    def get_last_version(self):
        return DocumentVersion.query().filter_by(document_id=self.id).order_by(DocumentVersion.id.desc()).first()


class DocumentVersion(BaseModel):
    __tablename__ = "document_version"

    document_id = Column(Integer, ForeignKey("document.id"), index=True)
    document = relationship("Document")

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    timestamp = Column(DateTime)
    comment = Column(String)

    data = Column(String)

    def __init__(self, **kwargs):
        kwargs["timestamp"] = datetime.now()
        super().__init__(**kwargs)

    def as_dict(self):
        return {
            "id": self.document.id,
            "namespace": self.document.namespace,
            "version_id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "comment": self.comment,
            "data": json.loads(self.data),
            "user": self.user.as_dict(),
            "protected": self.document.protected,
        }
