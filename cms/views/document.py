import json

from flask import request
from flask_restful import Resource

from cms.models.document import Document, DocumentVersion
from cms.database import database


class Documents(Resource):
    def get(self):
        # returns all documents
        return {"status": "ok", "documents": [], "count": 0}

    def put(self):
        """create an document"""
        body = request.get_json()

        data = body["document"]
        comment = body.get("comment", "creation")
        namespace = data.pop("namespace")

        document = Document(namespace=namespace)
        document.create()

        version = DocumentVersion(document_id=document.id, comment=comment, data=json.dumps(data))
        version.create()

        return {"status": "ok", "document": version.as_dict()}
