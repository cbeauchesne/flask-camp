Out of the box, the REST API provide search with limit/offset paraemters, and user tags. You will probably need to extend this feature. Here is the recipe to achieve that.

1. Define a database table that will store your search fields
2. Add a `before_document_save` that will fill this table on each document save
3. Add a `update_search_query` that will complete the SQL query for the `/documents` endpoint


```python

from flask import request
from flask_camp import RestApi, current_api
from flask_camp.models import BaseModel, Document
from sqlalchemy import Column, String, ForeignKey


class DocumentSearch(BaseModel):
    # Define a one-to-one relationship with document table
    # ondelete is mandatory, as a deletion of the document must delete the search item
    id = Column(ForeignKey(Document.id, ondelete='CASCADE'), index=True, nullable=True, primary_key=True)

    # We want to be able to search on a document type property
    # index is very import, obviously
    document_type = Column(String(16), index=True)


def before_document_save(document):
    if document.last_version is None:  # document as been merged
        delete(DocumentSearch).where(DocumentSearch.id == document.id)
        return

    version = document.last_version

    search_item = DocumentSearch.get(id=document.id)
    if search_item is None:  # means the document is not yet created
        search_item = DocumentSearch(id=document.id)
        current_api.database.session.add(search_item)

    if isinstance(version.data, dict):
        search_item.document_type = version.data.get("type")


def update_search_query(query):
    document_type = request.args.get("t", default=None, type=str)

    if document_type is not None:
        query = query.join(DocumentSearch).where(DocumentSearch.document_type == document_type)

    return query


app = Flask(__name__)
api = RestApi(app=app, before_document_save=before_document_save, update_search_query=update_search_query)
```
