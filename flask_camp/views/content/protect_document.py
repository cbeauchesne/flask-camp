from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp.models._document import Document
from flask_camp._services._security import allow

rule = "/protect_document/<int:document_id>"


@allow("moderator")
@schema("protect_document.json")
def post(document_id):
    """Protect/unprotect a document. The document won't be editable anymore, except for moderators"""
    document = Document.get(id=document_id, with_for_update=True)

    if document is None:
        raise NotFound()

    if document.is_redirection:
        raise BadRequest()

    protected = request.get_json()["protected"]

    if protected == document.protected:
        raise BadRequest("User is still blocked/unblocked")

    document.protected = protected

    current_api.add_log("protect" if protected else "unprotect", document=document)
    current_api.database.session.commit()

    document.clear_memory_cache()

    return {"status": "ok"}
