import json

from flask import request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from cms.decorators import allow
from cms.limiter import limiter
from cms.models.document import Document, DocumentVersion
from cms.schemas import schema

rule = "/document/<int:id>"


@allow("anonymous")
def get(id):
    version = DocumentVersion.query().filter_by(document_id=id).order_by(DocumentVersion.id.desc()).first()

    if version is None:
        raise NotFound()

    return {"status": "ok", "document": version.as_dict()}


@limiter.limit("2/second;10/minute;60/hour")
@allow("authenticated")
@schema("cms/schemas/modify_document.json")
def post(id):
    """add a new version to a document"""
    document = Document.get(id=id)

    if document is None:
        raise NotFound()

    if document.protected and not current_user.is_moderator:
        raise Forbidden("The document is protected")

    body = request.get_json()

    comment = body.get("comment", "")
    data = body["document"]["data"]

    version = DocumentVersion(document_id=document.id, user_id=current_user.id, comment=comment, data=json.dumps(data))
    version.create()

    return {"status": "ok", "document": version.as_dict()}
