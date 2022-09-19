import json
import logging

from flask import request, current_app, Response
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, Forbidden, Conflict

from cms.decorators import allow
from cms.limiter import limiter
from cms.models.document import Document, DocumentVersion
from cms.models.log import add_log
from cms.schemas import schema

log = logging.getLogger(__name__)

rule = "/document/<int:id>"


@allow("anonymous")
def get(id):

    document_as_dict = current_app.memory_cache.document.get(id)

    if document_as_dict is None:  # document is not known by mem cache
        document = Document.get(id=id)

        if document is None:
            raise NotFound()

        document_as_dict = document.as_dict()
        current_app.memory_cache.document.set(id, document_as_dict)

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
def post(id):
    """add a new version to a document"""
    document = Document.get(id=id)

    if document is None:
        raise NotFound()

    if document.protected and not current_user.is_moderator:
        raise Forbidden("The document is protected")

    body = request.get_json()

    comment = body.get("comment", "")
    data = body["document"]["data"]
    version_number = body["document"]["version_number"]

    old_version = document.as_dict()

    if old_version["version_number"] != version_number:
        raise Conflict("A new version exists")  # TODO give the new version

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
        if error_info[0] == "UNIQUE constraint failed: document_version.document_id, document_version.version_number":
            raise Conflict("A new version exists") from e  # TODO give the new version
        else:
            raise

    version_as_dict = version.as_dict()

    current_app.memory_cache.document.set(id, version_as_dict)

    return {"status": "ok", "document": version_as_dict}


@allow("admin")
@schema("cms/schemas/comment.json")
def delete(id):
    """delete a document"""
    document = Document.get(id=id)

    if document is None:
        raise NotFound()

    current_app.database.session.delete(document)

    add_log("delete_document", document_id=document.id)
    current_app.database.session.commit()

    current_app.memory_cache.document.delete(id)

    return {"status": "ok"}
