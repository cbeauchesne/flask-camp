from datetime import datetime

from flask import request, current_app
from flask_login import current_user
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from flask_camp.models import BaseModel
from flask_camp.models.user import User


def add_log(action, comment=None, target_user=None, document=None, merged_document=None, version=None):

    if comment is None:
        comment = request.get_json()["comment"]

    document_id = document.id if document is not None else None
    merged_document_id = merged_document.id if merged_document is not None else None
    version_id = version.id if version is not None else None

    log = Log(
        action=action,
        comment=comment,
        target_user=target_user,
        document_id=document_id,
        merged_document_id=merged_document_id,
        version_id=version_id,
    )
    current_app.database.session.add(log)


class Log(BaseModel):
    __tablename__ = "log"

    timestamp = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey(User.id), index=True)
    user = relationship(User, foreign_keys=[user_id])

    action = Column(String(32), nullable=False, index=True)
    comment = Column(String(128), nullable=False, index=True)

    target_user_id = Column(Integer, ForeignKey(User.id), index=True)
    target_user = relationship(User, foreign_keys=[target_user_id])

    # no foreign keys: deletion are possible
    document_id = Column(Integer, index=True)
    version_id = Column(Integer, index=True)
    merged_document_id = Column(Integer, index=True)

    def __init__(self, **kwargs):
        kwargs["timestamp"] = datetime.now()
        kwargs["user_id"] = current_user.id

        super().__init__(**kwargs)

    def as_dict(self):
        return {
            "user": self.user.as_dict(),
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "target_user_id": self.target_user_id,
            "target_user": None if self.target_user is None else self.target_user.as_dict(),
            "document_id": self.document_id,
            "merged_document_id": self.merged_document_id,
            "version_id": self.version_id,
        }
