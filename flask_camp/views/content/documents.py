from flask import request
from sqlalchemy import select, func
from werkzeug.exceptions import BadRequest

from flask_camp._schemas import schema
from flask_camp._utils import get_cooked_document, cook, current_api
from flask_camp._services._security import allow
from flask_camp.models._document import Document

rule = "/documents"


@allow("anonymous", "authenticated", allow_blocked=True)
def get():
    """Get a list of documents"""

    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    def make_query(base_query):

        query = base_query

        query = query.where(Document.redirect_to.is_(None))

        tag_filters_args = {
            "user_id": request.args.get("tag_user_id", default=None, type=int),
            "name": request.args.get("tag_name", default=None, type=str),
            "value": request.args.get("tag_value", default=None, type=str),
        }

        tag_filters_args = {k: v for k, v in tag_filters_args.items() if v is not None}

        if len(tag_filters_args) != 0:
            query = query.where(Document.user_tags.any(**tag_filters_args))

        query = current_api.update_search_query(query)

        return current_api.database.session.execute(query)

    count = make_query(select(func.count(Document.id)))
    document_ids = make_query(select(Document.id).limit(limit).offset(offset).order_by(Document.id.asc()))

    documents = [get_cooked_document(row[0]) for row in document_ids]
    return {"status": "ok", "documents": documents, "count": list(count)[0][0]}


@allow("authenticated")
@schema("create_document.json")
def put():
    """create an document"""
    body = request.get_json()

    current_api.validate_user_schemas(body["document"])

    document = Document.create(
        comment=body["comment"],
        data=body["document"]["data"],
    )

    current_api.database.session.flush()

    current_api.before_document_save(document)

    current_api.database.session.commit()

    document.clear_memory_cache()

    return {"status": "ok", "document": cook(document.last_version.as_dict())}
