from werkzeug.exceptions import NotFound, BadRequest

from cms import database
from cms.views.core import BaseResource
from cms.decorators import allow_moderator
from cms.models.document import DocumentVersion
from cms.models.log import add_log


class HideVersionView(BaseResource):
    @allow_moderator
    def put(self, id):
        version = DocumentVersion.get(id=id)

        if version is None:
            raise NotFound()

        if version.document.get_last_version().id == id:
            raise BadRequest("You can't hide the last version of a document")

        version.hidden = True
        add_log("hide_version", version_id=version.id, document_id=version.document.id)

        database.session.commit()

        return {"status": "ok"}

    @allow_moderator
    def delete(self, id):
        version = DocumentVersion.get(id=id)

        if version is None:
            raise NotFound()

        version.hidden = False
        add_log("unhide_version", version_id=version.id, document_id=version.document.id)

        database.session.commit()

        return {"status": "ok"}
