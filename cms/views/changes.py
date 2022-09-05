from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user

from cms.models.document import Document, DocumentVersion


class ChangesView(Resource):
    def get(self):
        # returns all changes
        filters = {}

        query = DocumentVersion.query()

        if "id" in request.args:
            filters["document_id"] = request.args.get("id", type=int)

        if len(filters) != 0:
            query = query.filter_by(**filters)

        query = query.order_by(DocumentVersion.id.desc())

        return {
            "status": "ok",
            "count": query.count(),
            "changes": [version.as_dict() for version in query],  # todo : do not include fields
        }
