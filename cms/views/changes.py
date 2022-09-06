from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest

from cms.models.document import Document, DocumentVersion


class ChangesView(Resource):
    def get(self):
        # returns all changes
        filters = {}

        limit = request.args.get("limit", default=30, type=int)
        offset = request.args.get("offset", default=0, type=int)

        if not 0 <= limit <= 100:
            raise BadRequest("Limit can't be lower than 0 or higher than 100")

        query = DocumentVersion.query()

        if "id" in request.args:
            filters["document_id"] = request.args.get("id", type=int)

        if len(filters) != 0:
            query = query.filter_by(**filters)

        query = query.order_by(DocumentVersion.id.desc())
        count = query.count()
        query = query.offset(offset).limit(limit)

        return {
            "status": "ok",
            "count": count,
            "changes": [version.as_dict() for version in query],  # todo : do not include fields
        }
