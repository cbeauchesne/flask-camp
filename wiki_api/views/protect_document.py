from flask import current_app, request
from werkzeug.exceptions import NotFound, BadRequest

from wiki_api.decorators import allow
from wiki_api.models.document import Document
from wiki_api.models.log import add_log
from wiki_api.schemas import schema

rule = "/protect_document/<int:document_id>"


@allow("moderator")
@schema("protect_document.json")
def post(document_id):
    """Protect/unprotect a document. The document won't be editable anymore, except for moderators"""
    document = Document.get(id=document_id, with_for_update=True)

    if document is None:
        raise NotFound()

    if document.redirect_to is not None:
        raise BadRequest()

    protected = request.get_json()["protected"]

    if protected == document.protected:
        raise BadRequest("User is still blocked/unblocked")

    document.protected = protected
    add_log("protect" if protected else "unprotect", document=document)

    current_app.database.session.commit()

    document.clear_memory_cache()

    return {"status": "ok"}
