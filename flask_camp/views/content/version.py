from flask import request
from werkzeug.exceptions import NotFound

from flask_camp._schemas import schema
from flask_camp._services._security import allow
from flask_camp._utils import cook, current_api, JsonResponse
from flask_camp.exceptions import CantHideLastVersion, CantDeleteLastVersion
from flask_camp.models import DocumentVersion

rule = "/document/version<int:version_id>"


@allow("anonymous", "authenticated", allow_blocked=True)
def get(version_id):
    """Get a given version of a document"""

    version = DocumentVersion.get(id=version_id)

    if version is None:
        raise NotFound()

    return JsonResponse({"status": "ok", "document": cook(version.as_dict())})


@allow("moderator")
@schema("modify_version.json")
def put(version_id):
    """Modify a version of a document. The only possible modification is hide/unhide a version"""
    version = DocumentVersion.get(id=version_id, with_for_update=True)

    if version is None:
        raise NotFound()

    version.hidden = request.get_json()["version"]["hidden"]

    if version.hidden and version.document.last_version_id == version.id:
        raise CantHideLastVersion()

    action = "hide_version" if version.hidden else "unhide_version"
    current_api.add_log(action, version=version, document=version.document)
    current_api.database.session.commit()

    return JsonResponse({"status": "ok"})


@allow("admin")
@schema("action_with_comment.json")
def delete(version_id):
    """Delete a version of a document (only for admins)"""
    version = DocumentVersion.get(id=version_id, with_for_update=True)

    if version is None:
        raise NotFound()

    if version.id == version.document.last_version_id:
        raise CantDeleteLastVersion()

    current_api.add_log("delete_version", version=version, document=version.document)
    current_api.database.session.delete(version)
    current_api.database.session.commit()

    return JsonResponse({"status": "ok"})
