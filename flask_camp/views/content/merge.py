from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp.models._document import Document, DocumentVersion
from flask_camp._services._security import allow

rule = "/merge"


@allow("moderator")
@schema("merge_documents.json")
def post():
    """Merge two documents. Merged document will become a redirection, and will be no longer modifiable
    Other document will get all hostory from merged"""

    data = request.get_json()
    document_to_merge = Document.get(id=data["document_to_merge"], with_for_update=True)
    document_destination = Document.get(id=data["document_destination"], with_for_update=True)

    if document_to_merge is None or document_destination is None:
        raise NotFound()

    if document_to_merge.id == document_destination.id:
        raise BadRequest()

    if document_destination.is_redirection or document_to_merge.is_redirection:
        raise BadRequest()

    document_to_merge.redirect_to = document_destination.id
    DocumentVersion.query.filter_by(document_id=document_to_merge.id).update({"document_id": document_destination.id})
    document_to_merge.last_version_id = None
    document_to_merge.last_version = None
    document_destination.update_last_version_id()

    current_api.before_document_save(document_to_merge)
    current_api.before_document_save(document_destination)
    current_api.add_log(
        "merge", comment=data["comment"], document=document_destination, merged_document=document_to_merge
    )
    current_api.database.session.commit()

    document_destination.clear_memory_cache()
    document_to_merge.clear_memory_cache()

    return {"status": "ok"}
