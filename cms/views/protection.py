import json

from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound, BadRequest

from cms.decorators import moderator_required
from cms.models.document import Document, DocumentVersion
from cms.schemas import schema


class ProtectionView(Resource):
    @moderator_required
    def put(self, id):
        doc = Document.query().filter_by(id=id).first()

        if doc is None:
            raise NotFound()

        doc.protected = True
        doc.update()

        return {"status": "ok"}

    @moderator_required
    def delete(self, id):
        doc = Document.query().filter_by(id=id).first()

        if doc is None:
            raise NotFound()

        doc.protected = False
        doc.update()

        return {"status": "ok"}
