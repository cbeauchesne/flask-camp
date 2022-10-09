from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from flask_camp.schemas import schema
from flask_camp.services.security import allow
from flask_camp.models.document import DocumentVersion, Document
from flask_camp.models.log import add_log
from flask_camp.services.database import database
from flask_camp.utils import cook

rule = "/version/<int:version_id>"


@allow("anonymous", "authenticated", allow_blocked=True)
def get(version_id):
    """Get a given version of a document"""

    version = DocumentVersion.get(id=version_id)

    if version is None:
        raise NotFound()

    return {"status": "ok", "document": cook(version.as_dict())}


@allow("moderator")
@schema("modify_version.json")
def post(version_id):
    """Modify a version of a document. The only possible modification is hide/unhide a version"""
    version = DocumentVersion.get(id=version_id)  # todo with for update

    if version is None:
        raise NotFound()

    hidden = request.get_json()["hidden"]
    version.hidden = hidden
    database.session.flush()

    document = Document.get(id=version.document_id, with_for_update=True)
    document.update_last_version_id()

    add_log("hide_version" if hidden else "unhide_version", version=version, document=version.document)

    database.session.commit()
    version.document.clear_memory_cache()  # todo : only if just hid the last version

    return {"status": "ok"}


@allow("admin")
@schema("action_with_comment.json")
def delete(version_id):
    """Delete a version of a document (only for admins)"""
    version = DocumentVersion.get(id=version_id)

    if version is None:
        raise NotFound()

    if DocumentVersion.query.filter_by(document_id=version.document_id).count() <= 1:
        raise BadRequest("Can't delete last version of a document")

    document = Document.get(id=version.document_id, with_for_update=True)

    document.update_last_version_id(forbidden_id=version.id)
    database.session.delete(version)

    add_log("delete_version", version=version, document=version.document)

    database.session.commit()
    version.document.clear_memory_cache()

    return {"status": "ok"}
