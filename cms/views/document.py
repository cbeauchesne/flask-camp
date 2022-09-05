import json

from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user

from cms.models.document import Document, DocumentVersion


class DocumentsView(Resource):
    def get(self):
        # returns all documents
        documents = DocumentVersion.query()
        count = DocumentVersion.query().count()

        # TODO : get only last version
        documents = [document.as_dict() for document in documents]
        return {"status": "ok", "documents": documents, "count": count}

    @login_required
    def put(self):
        """create an document"""
        body = request.get_json()

        data = body["document"]
        comment = body.get("comment", "creation")
        namespace = data.pop("namespace")

        document = Document(namespace=namespace)
        document.create()

        version = DocumentVersion(
            document_id=document.id, author_id=current_user.id, comment=comment, data=json.dumps(data)
        )
        version.create()

        return {"status": "ok", "document": version.as_dict()}


class DocumentView(Resource):
    def get(self, id):
        version = DocumentVersion.query().filter_by(document_id=id).order_by(DocumentVersion.id.desc()).first()
        return {"status": "ok", "document": version.as_dict()}
