import time

from flask import request
from flask_login import current_user
from werkzeug.exceptions import NotFound, Forbidden, BadRequest

from flask_camp._schemas import schema
from flask_camp._services._security import allow
from flask_camp._utils import get_cooked_document, cook, current_api, JsonResponse
from flask_camp.models._document import Document, DocumentVersion
from flask_camp.exceptions import EditConflict


rule = "/document/<int:document_id>"


@allow("anonymous", "authenticated", allow_blocked=True)
def get(document_id):
    """Get a document"""
    document_as_dict = get_cooked_document(document_id)  # it handles not found

    if document_as_dict.get("redirects_to"):
        return JsonResponse(
            data={"status": "ok", "document": document_as_dict},
            headers={"Location": f"/document/{document_as_dict['redirects_to']}"},
            status=301,
        )

    response = JsonResponse(data={"status": "ok", "document": document_as_dict}, add_etag=True)
    current_api.after_get_document(response=response)

    return response


@allow("authenticated")
@schema("add_new_version.json")
def post(document_id):
    """Add a new version to a document"""

    document = Document.get(id=document_id, with_for_update=True)

    if document is None:
        raise NotFound()

    if document.protected and not current_user.is_moderator:
        raise Forbidden("The document is protected")

    if document.is_redirection:
        raise BadRequest("The document is a redirection")

    old_version = document.last_version

    body = request.get_json()

    comment = body["comment"]
    data = body["document"]["data"]

    if document.id != body["document"]["id"]:
        raise BadRequest("Id in body does not match id in URI")

    version_id = body["document"]["version_id"]
    last_version_as_dict = document.as_dict()

    if last_version_as_dict["version_id"] != version_id:
        raise EditConflict(last_version=last_version_as_dict, your_version=body["document"])

    version = DocumentVersion(
        document=document,
        user=current_user,
        comment=comment,
        data=data,
    )

    current_api.database.session.add(version)
    document.last_version = version

    document.associated_ids = current_api.get_associated_ids(version.as_dict())

    assert _RACE_CONDITION_TESTING()

    current_api.database.session.flush()

    current_api.before_update_document(document=document, old_version=old_version, new_version=version)

    current_api.database.session.commit()

    document.clear_memory_cache()

    return JsonResponse({"status": "ok", "document": cook(version.as_dict())})


@allow("moderator")
@schema("modify_document.json")
def put(document_id):
    """Modify a document. Actually, only protect/unprotect it is possible"""
    document = Document.get(id=document_id, with_for_update=True)

    if document is None:
        raise NotFound()

    if document.is_redirection:
        raise BadRequest()

    protected = request.get_json()["document"]["protected"]

    if protected != document.protected:
        document.protected = protected

        current_api.add_log("protect" if protected else "unprotect", document=document)
        current_api.database.session.commit()

        document.clear_memory_cache()

    return JsonResponse({"status": "ok"})


@allow("admin")
@schema("action_with_comment.json")
def delete(document_id):
    """Delete a document"""

    document = Document.get(id=document_id)

    if not document:
        raise NotFound()

    current_api.before_delete_document(document=document)

    current_api.database.session.delete(document)

    current_api.add_log("delete_document", document=document)
    current_api.database.session.commit()

    document.clear_memory_cache()

    response = JsonResponse({"status": "ok"})
    current_api.after_delete_document(response=response)
    return response


def _RACE_CONDITION_TESTING():
    if "rc_sleep" in request.args:
        rc_sleep = float(request.args["rc_sleep"])
        time.sleep(rc_sleep)

    return True
