Out of the box, the REST API provide search with limit/offset paraemters, and user tags. You will probably need to extend this feature> Here is the recipe to achieve that.

1. Define a database table that will store your search fields
2. Add a `before_document_save` that will fill this table on each document save
3. Add a `update_search_query` that will complete the SQL query for the `/documents` endpoint


```python

from flask import request
from flask_camp import RestApi
from flask_camp.models import BaseModel, Document
from sqlalchemy import Column, String, ForeignKey


class DocumentSearch(BaseModel):
    # Define a one-to-one relationship with document table
    # ondelete is mandatory, as a deletion of the document must delete the search item
    id = Column(ForeignKey(Document.id, ondelete='CASCADE'), index=True, nullable=True, primary_key=True)

    # We want to be able to search on a namespace property
    # index is very import, obviously
    namespace = Column(String(16), index=True)


def before_document_save(version):

    search_item = DocumentSearch.get(id=version.document.id)
    if search_item is None:  # means the document is not yet created
        search_item = DocumentSearch(id=version.document.id)

        # we need to ass the item in the session
        database.session.add(search_item)

    search_item.namespace = version.data["namespace"]


def update_search_query(query):
    namespace = request.args.get("namespace", default=None, type=str)

    if namespace is not None:
        query = query.join(DocumentSearch).where(DocumentSearch.namespace == namespace)

    return query


app = Flask(__name__)
api = RestApi(app=app, before_document_save=before_document_save, update_search_query=update_search_query)
```
