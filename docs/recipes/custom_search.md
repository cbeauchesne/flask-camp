Out of the box, the REST API provide search with limit/offset paraemters, and user tags. You will probably need to extend this feature. Here is the recipe to achieve that.

1. Define a database table that will store your search fields
2. Add a `before_create_document`
3. Add a `before_update_document` that will fill this table on each document save
4. Add a `update_search_query` that will complete the SQL query for the `/documents` endpoint
5. Add a `before_merge_document` to remove search index for merged document

```python

from flask import request
from flask_camp import RestApi, current_api
from flask_camp.models import BaseModel, Document
from sqlalchemy import Column, String, ForeignKey


class DocumentSearch(BaseModel):
    # Define a one-to-one relationship with document table
    # ondelete is mandatory, as a deletion of the document must delete the search item
    id = Column(ForeignKey(Document.id, ondelete="CASCADE"), index=True, nullable=True, primary_key=True)

    # We want to be able to search on a document type property
    # index is very import, obviously
    document_type = Column(String(16), index=True)


def update_search_query(query):
    document_type = request.args.get("t", default=None, type=str)

    if document_type is not None:
        query = query.join(DocumentSearch).where(DocumentSearch.document_type == document_type)

    return query


def update_document_search(search_item, version):
    search_item.document_type = version.data.get("type")


app = Flask(__name__)
api = RestApi(app=app, update_search_query=update_search_query)


@api.before_create_document
def before_create_document(document):
    search_item = DocumentSearch(id=document.id)
    current_api.database.session.add(search_item)
    update_document_search(search_item, document.last_version)


@api.before_update_document
def before_update_document(document, old_version, new_version):  # pylint: disable=unused-argument
    update_document_search(DocumentSearch.get(id=document.id), new_version)


@api.before_merge_documents
def before_merge_documents(source_document, target_document):  # pylint: disable=unused-argument
    delete(DocumentSearch).where(DocumentSearch.id == source_document.id)
```
