import json
import logging

from flask import request, current_app, Response
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
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
    document = Document.get(id=document_id)

    if document is None:
        raise NotFound()

    if document.protected and not current_user.is_moderator:
        raise Forbidden("The document is protected")

    if document.redirect_to:
        raise BadRequest("The document is a redirection")

    body = request.get_json()

    comment = body.get("comment", "")
    data = body["document"]["data"]
    version_number = body["document"]["version_number"]

    last_version = document.as_dict()

    if last_version["version_number"] != version_number:
        raise EditConflict(last_version=last_version, your_version=body["document"])

    version = DocumentVersion(
        document_id=document.id,
        user_id=current_user.id,
        comment=comment,
        version_number=version_number + 1,
        data=json.dumps(data),
    )

    current_app.database.session.add(version)
    try:
        current_app.database.session.commit()
    except IntegrityError as e:
        error_info = e.orig.args
        if error_info[0] == "UNIQUE constraint failed: version.document_id, version.version_number":
            raise EditConflict(last_version=None, your_version=body["document"]) from e
        else:
            raise

    version_as_dict = version.as_dict()

    current_app.refresh_memory_cache(document_id)

    return {"status": "ok", "document": version_as_dict}


@allow("admin")
@schema("cms/schemas/comment.json")
def delete(document_id):
    """Delete a document"""
    document = Document.get(id=document_id)

    if document is None:
        raise NotFound()

    current_app.database.session.delete(document)

    add_log("delete_document", document=document)
    current_app.database.session.commit()

    current_app.refresh_memory_cache(document_id)

    return {"status": "ok"}
