# from sqlalchemy import Column
# from sqlalchemy import ForeignKey
# from sqlalchemy import Integer
# from sqlalchemy import String

# from sqlalchemy.orm import relationship

# from cms.models import BaseModel


# class Document(BaseModel):
#     __tablename__ = "document"

#     namespace = Column(String)

#     children = relationship("Child")


# class DocumentVersion(BaseModel):
#     __tablename__ = "document_version"

#     document_id = Column(Integer, ForeignKey("document.id"), index=True)

#     author_id = Column(Integer, )
#     timestamp
#     comment

#     data
