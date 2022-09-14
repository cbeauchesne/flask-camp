import json

from flask import request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from cms import database
from cms.decorators import allow
from cms.limiter import limiter
from cms.models.document import Document, DocumentVersion
from cms.models.log import add_log
from cms.schemas import schema

rule = "/document/<int:id>"


@allow("anonymous")
def get(id):
    document = Document.get(id=id)

    if document is None:
        raise NotFound()

    return {"status": "ok", "document": document.as_dict()}


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


@allow("admin")
@schema("cms/schemas/comment.json")
def delete(id):
    """delete a document"""
    document = Document.get(id=id)

    if document is None:
        raise NotFound()

    database.session.delete(document)

    add_log("delete_document", document_id=document.id)
    database.session.commit()

    return {"status": "ok"}
