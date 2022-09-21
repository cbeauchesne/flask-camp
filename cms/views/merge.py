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
    document_to_merge = Document.get(id=request.get_json()["document_to_merge"])
    document_destination = Document.get(id=request.get_json()["document_destination"])

    if document_to_merge is None or document_destination is None:
        raise NotFound()

    if document_to_merge.id == document_destination.id:
        raise BadRequest()

    add_log("merge", comment="TODO", document_id=document_destination.id, merged_document_id=document_to_merge.id)

    versions = DocumentVersion.query.filter(
        DocumentVersion.document_id.in_([document_destination.id, document_to_merge.id])
    ).order_by(DocumentVersion.id.asc())

    for i, version in enumerate(versions.all()):
        version.version_number = -(i + 1)

    current_app.database.session.flush()

    document_to_merge.redirect_to = document_destination.id
    DocumentVersion.query.filter_by(document_id=document_to_merge.id).update({"document_id": document_destination.id})

    current_app.database.session.flush()

    DocumentVersion.query.filter_by(document_id=document_destination.id).update(
        {DocumentVersion.version_number: -DocumentVersion.version_number}
    )

    current_app.database.session.commit()

    current_app.memory_cache.document.delete(document_destination.id)
    current_app.memory_cache.document.delete(document_to_merge.id)

    return {"status": "ok"}