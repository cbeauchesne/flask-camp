from flask import request
from werkzeug.exceptions import BadRequest

from flask_camp._utils import current_api
from flask_camp._services._security import allow
from flask_camp.models._document import DocumentVersion
from flask_camp.models._user import User
from flask_camp._utils import cook

rule = "/versions"


@allow("anonymous", "authenticated", allow_blocked=True)
def get():
    """Get a list of versions"""
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

    query = current_api.database.session.query(DocumentVersion)

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
        "versions": [cook(version.as_dict()) for version in versions],
    }
