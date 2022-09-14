from flask import request
from werkzeug.exceptions import BadRequest

from cms.decorators import allow
from cms.models.document import Document, DocumentVersion

rule = "/document_versions"


@allow("anonymous")
def get():
    # returns all changes
    filters = {}

    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)
    document_id = request.args.get("document_id", default=None, type=int)
    user_id = request.args.get("user_id", default=None, type=int)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    query = DocumentVersion.query()

    if document_id is not None:
        filters["document_id"] = document_id

    if user_id is not None:
        filters["user_id"] = user_id

    if len(filters) != 0:
        query = query.filter_by(**filters)

    query = query.order_by(DocumentVersion.id.desc())
    count = query.count()
    query = query.offset(offset).limit(limit)

    return {
        "status": "ok",
        "count": count,
        "changes": [version.as_dict() for version in query],
    }
