from flask import request, current_app
from werkzeug.exceptions import BadRequest

from cms.decorators import allow
from cms.models.document import DocumentVersion
from cms.models.user import User

rule = "/versions"


@allow("anonymous")
def get():
    """GEt a list of versions"""
    filters = {}

    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)
    document_id = request.args.get("document_id", default=None, type=int)
    user_id = request.args.get("user_id", default=None, type=str)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    tag_filters_args = {
        "user_id": request.args.get("tag_user_id", default=None, type=int),
        "name": request.args.get("tag_name", default=None, type=str),
        "value": request.args.get("tag_value", default=None, type=str),
    }

    tag_filters_args = {k: v for k, v in tag_filters_args.items() if v is not None}

    query = current_app.database.session.query(DocumentVersion)

    if len(tag_filters_args) != 0:
        query = query.filter(DocumentVersion.user_tags.any(**tag_filters_args))

    if document_id is not None:
        filters["document_id"] = document_id

    if len(filters) != 0:
        query = query.filter_by(**filters)

    if user_id is not None:
        query = query.join(User).filter(User.id == user_id)

    query = query.order_by(DocumentVersion.id.desc())
    count = query.count()
    versions = query.offset(offset).limit(limit)

    return {
        "status": "ok",
        "count": count,
        "versions": [current_app.cook(version.as_dict()) for version in versions],
    }
