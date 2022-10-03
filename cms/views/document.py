import json
import logging
import time

from flask import request, current_app, Response
from flask_login import current_user
from werkzeug.exceptions import NotFound, Forbidden, Conflict, BadRequest

from cms.decorators import allow
from cms.limiter import limiter
from cms.models.document import Document, DocumentVersion
from cms.models.log import add_log
from cms.schemas import schema

log = logging.getLogger(__name__)

rule = "/document/<int:document_id>"


class EditConflict(Conflict):
    def __init__(self, your_version, last_version):
        super().__init__("A new version exists")
        self.data = {
            "last_version": last_version,
            "your_version": your_version,
        }


@allow("anonymous")
def get(document_id):
    """Get a document"""
    document_as_dict = current_app.get_cooked_document(document_id)  # it handles not found

    if "redirect_to" in document_as_dict:
        return Response(headers={"Location": f"/document/{document_as_dict['redirect_to']}"}, status=301)

    response = Response(
        response=json.dumps({"status": "ok", "document": document_as_dict}),
        content_type="application/json",
    )

    response.add_etag()
    response.make_conditional(request)

    return response


@limiter.limit("2/second;10/minute;60/hour")
@allow("authenticated")
@schema("cms/schemas/modify_document.json")
def post(document_id):
    """add a new version to a document"""

    document = Document.get(id=document_id, with_for_update=True)

    if document is None:
        raise NotFound()

    if document.protected and not current_user.is_moderator:
        raise Forbidden("The document is protected")

    if document.redirect_to:
        raise BadRequest("The document is a redirection")

    body = request.get_json()

    comment = body.get("comment", "")
    data = body["document"]["data"]
    version_id = body["document"]["version_id"]

    last_version = document.as_dict()

    if last_version["version_id"] != version_id:
        raise EditConflict(last_version=last_version, your_version=body["document"])

    version = DocumentVersion(
        document=document,
        user=current_user,
        comment=comment,
        data=json.dumps(data),
    )

    current_app.database.session.add(version)

    document.last_version = version
    document.associated_ids = current_app.get_associated_ids(version.as_dict())

    assert _RACE_CONDITION_TESTING()
    current_app.database.session.commit()

    document.clear_memory_cache()
    cooked_document = current_app.cook(version.as_dict())

    return {"status": "ok", "document": cooked_document}


@allow("admin")
@schema("cms/schemas/comment.json")
def delete(document_id):
    """Delete a document"""
    document = Document.get(id=document_id)

    if document is None:
        raise NotFound()

    current_app.database.session.delete(document)

    add_log("delete_document", document=document)

    current_app.database.session.flush()
    current_app.database.session.commit()

    document.clear_memory_cache()

    return {"status": "ok"}


def _RACE_CONDITION_TESTING():
    if "rc_sleep" in request.args:
        rc_sleep = float(request.args["rc_sleep"])
        time.sleep(rc_sleep)

    return True
