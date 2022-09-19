from flask import current_app
from werkzeug.exceptions import NotFound

from cms.decorators import allow
from cms.models.document import Document
from cms.models.log import add_log
from cms.schemas import schema

rule = "/protect_document/<int:id>"


@allow("moderator")
@schema("cms/schemas/comment.json")
def put(id):
    doc = Document.query().filter_by(id=id).first()

    if doc is None:
        raise NotFound()

    doc.protected = True
    add_log("protect", document_id=id)
    current_app.database.session.commit()

    current_app.memory_cache.document.delete(id)

    return {"status": "ok"}


@allow("moderator")
@schema("cms/schemas/comment.json")
def delete(id):
    doc = Document.query().filter_by(id=id).first()

    if doc is None:
        raise NotFound()

    doc.protected = False
    add_log("unprotect", document_id=id)
    current_app.database.session.commit()

    current_app.memory_cache.document.delete(id)

    return {"status": "ok"}
