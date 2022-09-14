from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from cms import database
from cms.schemas import schema
from cms.decorators import allow
from cms.models.document import DocumentVersion
from cms.models.log import add_log

rule = "/document_version/<int:id>"


@allow("anonymous")
def get(id):

    version = DocumentVersion.get(id=id)

    if version is None:
        raise NotFound()

    return {"status": "ok", "document": version.as_dict()}


@allow("admin")
@schema("cms/schemas/delete_version.json")
def delete(id):

    body = request.get_json()

    comment = body["comment"]

    version = DocumentVersion.get(id=id)

    if version is None:
        raise NotFound()

    if DocumentVersion.query().filter_by(document_id=version.document_id).count() <= 1:
        raise BadRequest("Can't delete last version of a document")

    add_log("delete_version", version_id=version.id, document_id=version.document.id)
    database.session.delete(version)

    database.session.commit()

    return {"status": "ok"}
