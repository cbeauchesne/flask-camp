import json

from flask import request, current_app
from flask_login import current_user
from sqlalchemy import select, func
from werkzeug.exceptions import BadRequest

from cms.decorators import allow
from cms.limiter import limiter
from cms.models.document import Document, DocumentVersion
from cms.schemas import schema

rule = "/documents"


@allow("anonymous")
def get():
    """Get a list of documents"""

    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    def make_query(base_query):
        return current_app.database.session.execute(base_query)

    count = make_query(select(func.count(Document.id)))
    document_ids = make_query(select(Document.id).limit(limit).offset(offset).order_by(Document.id.asc()))

    documents = [current_app.get_cooked_document(row[0]) for row in document_ids]
    return {"status": "ok", "documents": documents, "count": list(count)[0][0]}


@limiter.limit("1/second;10/minute;60/hour")
@allow("authenticated")
@schema("cms/schemas/create_document.json")
def put():
    """create an document"""
    body = request.get_json()

    comment = body.get("comment", "creation")
    namespace = body["document"]["namespace"]
    data = body["document"]["data"]

    document = Document(namespace=namespace)

    version = DocumentVersion(document=document, user=current_user, comment=comment, data=json.dumps(data))

    document.last_version = version
    document.associated_ids = current_app.get_associated_ids(version.as_dict())

    current_app.database.session.add(document)
    current_app.database.session.add(version)

    current_app.database.session.commit()

    current_app.refresh_memory_cache(document.id)

    return {"status": "ok", "document": current_app.cook(version.as_dict())}
