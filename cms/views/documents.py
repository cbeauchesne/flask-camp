import json

from flask import request, current_app
from flask_login import current_user
from werkzeug.exceptions import BadRequest

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

    tag_filters_args = {
        "user_id": request.args.get("tag_user_id", default=None, type=int),
        "name": request.args.get("tag_name", default=None, type=str),
        "value": request.args.get("tag_value", default=None, type=str),
    }

    tag_filters_args = {k: v for k, v in tag_filters_args.items() if v is not None}

    query = current_app.database.session.query(Document)

    if len(tag_filters_args) != 0:
        query = query.filter(Document.user_tags.any(**tag_filters_args))

    count = query.count()
    documents = query.offset(offset).limit(limit)

    documents = [document.as_dict() for document in documents]
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

    version = DocumentVersion(
        document=document, user=current_user, comment=comment, version_number=1, data=json.dumps(data)
    )

    current_app.database.session.add(document)
    current_app.database.session.add(version)

    current_app.database.session.commit()

    return {"status": "ok", "document": version.as_dict()}
