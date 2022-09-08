import json

from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from cms.decorators import allow_moderator
from cms.models.document import Document, DocumentVersion
from cms.schemas import schema
from cms.views.core import BaseResource


class ProtectionView(BaseResource):
    @allow_moderator
    def put(self, id):
        doc = Document.query().filter_by(id=id).first()

        if doc is None:
            raise NotFound()

        doc.protected = True
        doc.update()

        return {"status": "ok"}

    @allow_moderator
    def delete(self, id):
        doc = Document.query().filter_by(id=id).first()

        if doc is None:
            raise NotFound()

        doc.protected = False
        doc.update()

        return {"status": "ok"}
