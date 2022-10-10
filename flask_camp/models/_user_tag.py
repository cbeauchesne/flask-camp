"""user tag is ..."""

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from flask_camp.models._base_model import BaseModel
from flask_camp.models._user import User


class UserTag(BaseModel):
    __tablename__ = "user_tag"

    user_id = Column(Integer, ForeignKey(User.id), index=True, nullable=False)
    user = relationship(User, foreign_keys=[user_id])

    document_id = Column(Integer, ForeignKey("document.id"), index=True, nullable=False)
    document = relationship("Document", foreign_keys=[document_id])

    name = Column(String(16), index=True, nullable=False)
    value = Column(String(32), index=True)

    __table_args__ = (UniqueConstraint("user_id", "document_id", "name", name="_user_tag_uc"),)

    def as_dict(self):
        return {
            "user_id": self.user_id,
            "document_id": self.document_id,
            "name": self.name,
            "value": self.value,
        }
