Requirements

Recent change
   doc id/type
   version
   comment
   timestamp
   author

get version
    doc id type
    version




<Document>
    id
    type
    protected

<DocumentVersion>
    id  -> version id
    document_id -> Document.id
    hidden  # only mutable field

    



    author_id
    timestamp
    comment

    childs[]
    ...

Associations
    parent_id
    child_id


api/core.py:1: in <module>
    from cms import Application
cms/__init__.py:10: in <module>
    from .views.user import Users, UserValidation, UserLogin, UserLogout
cms/views/user.py:9: in <module>
    from cms.models.user import User as UserModel
cms/models/__init__.py:1: in <module>
    from ._base_model import BaseModel
cms/models/_base_model.py:6: in <module>
    from cms import database
E   ImportError: cannot import name 'database' from partially initialized module 'cms' (most likely due to a circular import) (/Users/charles.debeauchesne/repos/wiki_api/cms/__init__.py)