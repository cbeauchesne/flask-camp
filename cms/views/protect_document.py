import json

from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from cms import database
from cms.decorators import allow_moderator
from cms.models.document import Document, DocumentVersion
from cms.models.log import add_log
from cms.schemas import schema
from cms.views.core import BaseResource


class ProtectDocumentView(BaseResource):
    @allow_moderator
    def put(self, id):
        doc = Document.query().filter_by(id=id).first()

        if doc is None:
            raise NotFound()

        doc.protected = True
        add_log("protect", document_id=id)
        database.session.commit()

        return {"status": "ok"}

    @allow_moderator
    def delete(self, id):
        doc = Document.query().filter_by(id=id).first()

        if doc is None:
            raise NotFound()

        doc.protected = False
        add_log("unprotect", document_id=id)
        database.session.commit()

        return {"status": "ok"}
