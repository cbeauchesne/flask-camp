import json
from datetime import datetime

from flask_login import current_user
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from cms.models import BaseModel


def _as_dict(document, version, include_hidden_data_for_staff=False):
    result = {
        "id": document.id,
        "namespace": document.namespace,
        "protected": document.protected,
        "comment": version.comment,
        "hidden": version.hidden,
        "timestamp": version.timestamp.isoformat(),
        "user": version.user.as_dict(),
        "version_id": version.id,
    }

    if not version.hidden:
        result["data"] = json.loads(version.data)
    elif (
        include_hidden_data_for_staff
        and current_user.is_authenticated
        and (current_user.is_admin or current_user.is_moderator)
    ):
        result["data"] = json.loads(version.data)

    return result


class Document(BaseModel):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String(16), index=True)

    protected = Column(Boolean, nullable=False, default=False)

    user_tags = relationship("UserTag", back_populates="document", lazy="select")

    def as_dict(self):
        version = (
            DocumentVersion.query()
            .filter_by(document_id=self.id, hidden=False)
            .order_by(DocumentVersion.id.desc())
            .first()
        )
        if version is None:
            version = DocumentVersion.query().filter_by(document_id=self.id).order_by(DocumentVersion.id.desc()).first()

        return _as_dict(self, version)


class DocumentVersion(BaseModel):
    __tablename__ = "document_version"

    document_id = Column(Integer, ForeignKey("document.id"), index=True)
    document = relationship("Document")

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    timestamp = Column(DateTime)
    comment = Column(String)

    hidden = Column(Boolean, default=False, nullable=False)
    data = Column(String)

    def __init__(self, **kwargs):
        kwargs["timestamp"] = datetime.now()
        super().__init__(**kwargs)

    def as_dict(self):
        return _as_dict(self.document, self, include_hidden_data_for_staff=True)
