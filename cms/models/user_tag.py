"""user tag is ..."""

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from cms.models import BaseModel


class UserTag(BaseModel):
    __tablename__ = "user_tag"

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User", foreign_keys=[user_id])

    document_id = Column(Integer, ForeignKey("document.id"), index=True, nullable=False)
    document = relationship("Document", foreign_keys=[document_id])

    name = Column(String(16), index=True, nullable=False)
    value = Column(String(32))

    __table_args__ = (UniqueConstraint("user_id", "document_id", "name", name="_user_tag_uc"),)

    def as_dict(self):
        return {
            "user_id": self.user_id,
            "document_id": self.document_id,
            "name": self.name,
            "value": self.value,
            # "user": self.user.as_dict(),
            # "document": self.document.get_last_version().as_dict(),
        }
