from flask import request, current_app
from werkzeug.exceptions import NotFound, BadRequest

from cms.schemas import schema
from cms.decorators import allow
from cms.models.document import Document, DocumentVersion
from cms.models.log import add_log

rule = "/merge"


@allow("moderator")
@schema("cms/schemas/merge_documents.json")
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

    document_to_merge.redirect_to = document_destination.id
    DocumentVersion.query.filter_by(document_id=document_to_merge.id).update({"document_id": document_destination.id})
    document_to_merge.last_version_id = None
    document_destination.update_last_version_id()

    add_log("merge", comment=data["comment"], document=document_destination, merged_document=document_to_merge)

    current_app.database.session.commit()

    current_app.refresh_memory_cache(document_destination.id)
    current_app.refresh_memory_cache(document_to_merge.id)

    return {"status": "ok"}
