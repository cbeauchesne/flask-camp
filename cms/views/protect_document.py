from flask import current_app
from werkzeug.exceptions import NotFound, BadRequest

from cms.decorators import allow
from cms.models.document import Document
from cms.models.log import add_log
from cms.schemas import schema

rule = "/protect_document/<int:document_id>"


@allow("moderator")
@schema("cms/schemas/comment.json")
def put(document_id):
    """Protect a document. The document won't be editable anymore, excpet for moderators"""
    document = Document.query.filter_by(id=document_id).first()

    if document is None:
        raise NotFound()

    if document.redirect_to is not None:
        raise BadRequest()

    document.protected = True
    add_log("protect", document=document)  # TODO comment
    current_app.database.session.commit()

    current_app.refresh_memory_cache(document.id)

    return {"status": "ok"}


@allow("moderator")
@schema("cms/schemas/comment.json")
def delete(document_id):
    """Un-protect a document"""
    document = Document.query.filter_by(id=document_id).first()

    if document is None:
        raise NotFound()

    if document.redirect_to is not None:
        raise BadRequest()

    document.protected = False
    add_log("unprotect", document=document)
    current_app.database.session.commit()

    current_app.refresh_memory_cache(document.id)

    return {"status": "ok"}
