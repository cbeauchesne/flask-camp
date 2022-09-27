from flask import request, current_app
from werkzeug.exceptions import NotFound, BadRequest

from cms.schemas import schema
from cms.decorators import allow
from cms.models.document import DocumentVersion
from cms.models.log import add_log

rule = "/version/<int:version_id>"


@allow("anonymous")
def get(version_id):
    """Get a given version of a document"""

    version = DocumentVersion.get(id=version_id)

    if version is None:
        raise NotFound()

    return {"status": "ok", "document": version.as_dict()}


@allow("moderator")
@schema("cms/schemas/modify_version.json")
def post(version_id):
    """Modify a version of a document. The only possible modification is hide/unhide a version"""
    version = DocumentVersion.get(id=version_id)

    if version is None:
        raise NotFound()

    hidden = request.get_json()["hidden"]
    version.hidden = hidden

    add_log("hide_version" if hidden else "unhide_version", version=version, document=version.document)

    current_app.database.session.commit()
    current_app.refresh_memory_cache(version.document.id)

    return {"status": "ok"}


@allow("admin")
@schema("cms/schemas/comment.json")
def delete(version_id):
    """Delete a version of a document (only for admins)"""
    version = DocumentVersion.get(id=version_id)

    if version is None:
        raise NotFound()

    if DocumentVersion.query.filter_by(document_id=version.document_id).count() <= 1:
        raise BadRequest("Can't delete last version of a document")

    add_log("delete_version", version=version, document=version.document)

    current_app.database.session.delete(version)
    current_app.database.session.commit()
    current_app.refresh_memory_cache(version.document.id)

    return {"status": "ok"}
