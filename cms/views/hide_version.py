from werkzeug.exceptions import NotFound, BadRequest

from cms import database
from cms.decorators import allow
from cms.models.document import DocumentVersion
from cms.models.log import add_log

rule = "/hide_version/<int:id>"


@allow("moderator")
def put(id):
    version = DocumentVersion.get(id=id)

    if version is None:
        raise NotFound()

    version.hidden = True
    add_log("hide_version", version_id=version.id, document_id=version.document.id)

    database.session.commit()

    return {"status": "ok"}


@allow("moderator")
def delete(id):
    version = DocumentVersion.get(id=id)

    if version is None:
        raise NotFound()

    version.hidden = False
    add_log("unhide_version", version_id=version.id, document_id=version.document.id)

    database.session.commit()

    return {"status": "ok"}
