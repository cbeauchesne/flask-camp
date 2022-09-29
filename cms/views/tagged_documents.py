from flask import request, current_app
from werkzeug.exceptions import BadRequest

from cms.decorators import allow
from cms.models.document import Document


rule = "/tagged_documents"


@allow("anonymous")
def get():
    """Get a list of tagged documents"""

    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    tag_filters_args = {
        "user_id": request.args.get("tag_user_id", default=None, type=int),
        "name": request.args.get("tag_name", default=None, type=str),
        "value": request.args.get("tag_value", default=None, type=str),
    }

    tag_filters_args = {k: v for k, v in tag_filters_args.items() if v is not None}

    query = current_app.database.session.query(Document)  # TODO get only id

    if len(tag_filters_args) != 0:
        query = query.filter(Document.user_tags.any(**tag_filters_args))

    count = query.count()
    documents = query.offset(offset).limit(limit)

    documents = [current_app.get_cooked_document(document.id) for document in documents]
    return {"status": "ok", "documents": documents, "count": count}
