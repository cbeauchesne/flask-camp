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
    document_to_merge = Document.get(id=data["document_to_merge"], with_for_update=True)
    document_destination = Document.get(id=data["document_destination"], with_for_update=True)

    if document_to_merge is None or document_destination is None:
        raise NotFound()

    if document_to_merge.id == document_destination.id:
        raise BadRequest()

    if document_destination.is_redirection or document_to_merge.is_redirection:
        raise BadRequest()

    destination_old_version = document_destination.last_version

    document_to_merge.redirects_to = document_destination.id
    DocumentVersion.query.filter_by(document_id=document_to_merge.id).update({"document_id": document_destination.id})
    Tag.query.filter_by(document_id=document_to_merge.id).update({"document_id": document_destination.id})
    document_to_merge.last_version_id = None
    document_to_merge.last_version = None
    document_destination.update_last_version_id()

    current_api.before_merge_documents(document_to_merge=document_to_merge, document_destination=document_destination)

    if destination_old_version.id != document_destination.last_version.id:
        current_api.before_update_document(
            document=document_destination,
            old_version=destination_old_version,
            new_version=document_destination.last_version,
        )

    current_api.add_log(
        "merge", comment=data["comment"], document=document_destination, merged_document=document_to_merge
    )
    current_api.database.session.commit()

    document_destination.clear_memory_cache()
    document_to_merge.clear_memory_cache()

    response = JsonResponse({"status": "ok"})
    current_api.after_merge_documents(response=response)
    return response
