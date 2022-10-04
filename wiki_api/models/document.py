import json
from datetime import datetime

from flask import current_app
from flask_login import current_user
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from werkzeug.exceptions import BadRequest

from wiki_api.models import BaseModel
from wiki_api.models.user_tag import UserTag
from wiki_api.models.user import User


def _as_dict(document, version, include_hidden_data_for_staff=False):

    if document.redirect_to:
        return {"id": document.id, "redirect_to": document.redirect_to}

    result = {
        "id": document.id,
        "namespace": document.namespace,
        "protected": document.protected,
        "comment": version.comment,
        "hidden": version.hidden,
        "timestamp": version.timestamp.isoformat(),
        "user": version.user.as_dict(),
        "last_version_id": document.last_version_id,
        "version_id": version.id,
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

    user_tags = relationship(UserTag, back_populates="document", lazy="select", cascade="all,delete")
    versions = relationship(
        lambda: DocumentVersion,
        primaryjoin=lambda: Document.id == DocumentVersion.document_id,
        backref="document",
        lazy="select",
        cascade="all,delete",
    )

    last_version_id = Column(Integer, ForeignKey("version.id", use_alter=True))
    last_version = relationship(
        lambda: DocumentVersion,
        primaryjoin=lambda: Document.last_version_id == DocumentVersion.id,
        uselist=False,
        post_update=True,
    )

    redirect_to = Column(Integer, ForeignKey("document.id"))

    associated_ids = Column(ARRAY(Integer), index=True)

    def update_last_version_id(self, forbidden_id=None):
        """call this when a version has been hidden or deleted"""
        query = DocumentVersion.query

        if forbidden_id is not None:
            query = query.filter(DocumentVersion.id != forbidden_id)

        query = query.filter_by(document_id=self.id, hidden=False).order_by(DocumentVersion.id.desc())
        self.last_version = query.first()

        if self.last_version is None:
            raise BadRequest("There is no visible version associated with this document")

    def clear_memory_cache(self):
        current_app.memory_cache.delete_document(self.id)

        query = select(Document.id).where(Document.associated_ids.contains([self.id]))
        for row in current_app.database.session.execute(query):
            current_app.memory_cache.delete_document(row[0])

    def as_dict(self):
        return _as_dict(self, self.last_version)


class DocumentVersion(BaseModel):
    __tablename__ = "version"

    document_id = Column(Integer, ForeignKey("document.id"), index=True)
    # document = relationship("Document", foreign_keys=[document_id], back_populates="versions")

    user_id = Column(Integer, ForeignKey(User.id), index=True)
    user = relationship(User)

    timestamp = Column(DateTime)
    comment = Column(String)

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

    def __init__(self, **kwargs):
        kwargs["timestamp"] = datetime.now()
        super().__init__(**kwargs)

    def as_dict(self):
        return _as_dict(self.document, self, include_hidden_data_for_staff=True)
