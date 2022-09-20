import json
from datetime import datetime

from flask_login import current_user
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from cms.models import BaseModel
from cms.models.user_tag import UserTag


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
        "version_number": version.version_number,
    }

    if not version.hidden:
        result["data"] = json.loads(version.data)
    elif include_hidden_data_for_staff and (current_user.is_admin or current_user.is_moderator):
        result["data"] = json.loads(version.data)

    return result


class Document(BaseModel):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String(16), index=True)

    protected = Column(Boolean, nullable=False, default=False)

    user_tags = relationship("UserTag", back_populates="document", lazy="select", cascade="all,delete")
    versions = relationship("DocumentVersion", back_populates="document", lazy="select", cascade="all,delete")

    redirect_to = Column(Integer, ForeignKey("document.id"))

    def as_dict(self):
        version = (
            DocumentVersion.query()
            .filter_by(document_id=self.id, hidden=False)
            .order_by(DocumentVersion.id.desc())
            .first()
        )
        if version is None:  # can happen if all are hidden
            version = DocumentVersion.query().filter_by(document_id=self.id).order_by(DocumentVersion.id.desc()).first()

        return _as_dict(self, version)


class DocumentVersion(BaseModel):
    __tablename__ = "version"

    document_id = Column(Integer, ForeignKey("document.id"), index=True)
    document = relationship("Document")

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    timestamp = Column(DateTime)
    comment = Column(String)

    # This column give the nth version of a document
    # it starts at 1, and is incremented by 1 every new version
    # the api is responsible to increment it. By this, it prevents edit conflict
    version_number = Column(Integer, nullable=False)

    hidden = Column(Boolean, default=False, nullable=False)
    data = Column(String)

    user_tags = relationship(
        "UserTag",
        lazy="select",
        foreign_keys="DocumentVersion.document_id",
        primaryjoin=document_id == UserTag.document_id,
        uselist=True,
        viewonly=True,
    )

    __table_args__ = (UniqueConstraint("document_id", "version_number", name="_version_uc"),)

    def __init__(self, **kwargs):
        kwargs["timestamp"] = datetime.now()
        super().__init__(**kwargs)

    def as_dict(self):
        return _as_dict(self.document, self, include_hidden_data_for_staff=True)
