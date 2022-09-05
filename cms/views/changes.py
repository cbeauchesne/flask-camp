from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user

from cms.models.document import Document, DocumentVersion


class ChangesView(Resource):
    def get(self):
        # returns all changes
        versions = DocumentVersion.query()
        count = DocumentVersion.query().count()

        return {
            "status": "ok",
            "changes": [version.as_dict() for version in versions],  # todo : do not include fields
            "count": count,
        }
