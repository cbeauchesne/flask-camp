import json

from flask import request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from cms.decorators import allow
from cms.limiter import limiter
from cms.models.document import Document, DocumentVersion
from cms.schemas import schema

rule = "/documents"


@allow("anonymous")
def get():
    # returns all documents

    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    documents = Document.query().limit(limit).offset(offset)
    count = Document.query().count()

    documents = [document.get_last_version().as_dict() for document in documents]
    return {"status": "ok", "documents": documents, "count": count}


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
    document.create()

    version = DocumentVersion(document_id=document.id, user_id=current_user.id, comment=comment, data=json.dumps(data))
    version.create()

    return {"status": "ok", "document": version.as_dict()}
