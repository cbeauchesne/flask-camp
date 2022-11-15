from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from flask_camp._schemas import schema
from flask_camp._services._security import allow
from flask_camp._utils import current_api, JsonResponse
from flask_camp.models._document import Document, DocumentVersion
from flask_camp.models._tag import Tag

rule = "/documents/merge"


@allow("moderator")
@schema("merge_documents.json")
def put():
    """Merge two documents. Merged document will become a redirection, and will be no longer modifiable
    Other document will get all history from merged"""

    data = request.get_json()
    source_document = Document.get(id=data["source_document_id"], with_for_update=True)
    target_document = Document.get(id=data["target_document_id"], with_for_update=True)

    if source_document is None or target_document is None:
        raise NotFound()

    if source_document.id == target_document.id:
        raise BadRequest()

    if target_document.is_redirection or source_document.is_redirection:
        raise BadRequest()

    current_api.before_merge_documents.fire(source_document=source_document, target_document=target_document)

    destination_old_version = target_document.last_version

    source_document.redirects_to = target_document.id
    DocumentVersion.query.filter_by(document_id=source_document.id).update({"document_id": target_document.id})
    Tag.query.filter_by(document_id=source_document.id).update({"document_id": target_document.id})
    source_document.last_version_id = None
    source_document.last_version = None
    target_document.update_last_version_id()

    if destination_old_version.id != target_document.last_version.id:
        current_api.before_update_document.fire(
            document=target_document,
            old_version=destination_old_version,
            new_version=target_document.last_version,
        )

    current_api.add_log("merge", comment=data["comment"], document=target_document, merged_document=source_document)
    current_api.database.session.commit()

    target_document.clear_memory_cache()
    source_document.clear_memory_cache()

    response = JsonResponse({"status": "ok"})
    current_api.after_merge_documents.fire(response=response)
    return response
