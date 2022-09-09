import json

from flask import request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from cms.decorators import allow_anonymous, allow_authenticated
from cms.models.document import Document, DocumentVersion
from cms.schemas import schema
from cms.views.core import BaseResource


class DocumentsView(BaseResource):
    @allow_anonymous
    def get(self):
        # returns all documents

        limit = request.args.get("limit", default=30, type=int)
        offset = request.args.get("offset", default=0, type=int)

        if not 0 <= limit <= 100:
            raise BadRequest("Limit can't be lower than 0 or higher than 100")

        documents = Document.query().limit(limit).offset(offset)
        count = Document.query().count()

        documents = [document.get_last_version().as_dict() for document in documents]
        return {"status": "ok", "documents": documents, "count": count}

    @allow_authenticated
    @schema("cms/schemas/create_document.json")
    def put(self):
        """create an document"""
        body = request.get_json()

        comment = body.get("comment", "creation")
        namespace = body["document"]["namespace"]
        data = body["document"]["data"]

        document = Document(namespace=namespace)
        document.create()

        version = DocumentVersion(
            document_id=document.id, user_id=current_user.id, comment=comment, data=json.dumps(data)
        )
        version.create()

        return {"status": "ok", "document": version.as_dict()}


class DocumentView(BaseResource):
    @allow_anonymous
    def get(self, id):
        version = DocumentVersion.query().filter_by(document_id=id).order_by(DocumentVersion.id.desc()).first()

        if version is None:
            raise NotFound()

        return {"status": "ok", "document": version.as_dict()}

    @allow_authenticated
    @schema("cms/schemas/modify_document.json")
    def post(self, id):
        """add a new version to a document"""
        document = Document.get(id=id)

        if document is None:
            raise NotFound()

        if document.protected and not current_user.is_moderator:
            raise Forbidden("The document is protected")

        body = request.get_json()

        comment = body.get("comment", "")
        data = body["document"]["data"]

        version = DocumentVersion(
            document_id=document.id, user_id=current_user.id, comment=comment, data=json.dumps(data)
        )
        version.create()

        return {"status": "ok", "document": version.as_dict()}
