import json

from flask import request, current_app
from flask_login import current_user
from sqlalchemy import select, func
from werkzeug.exceptions import BadRequest

from flask_camp.services.security import allow
from flask_camp.models.document import Document, DocumentVersion
from flask_camp.schemas import schema

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

        return current_app.database.session.execute(query)

    count = make_query(select(func.count(Document.id)))
    document_ids = make_query(select(Document.id).limit(limit).offset(offset).order_by(Document.id.asc()))

    documents = [current_app.get_cooked_document(row[0]) for row in document_ids]
    return {"status": "ok", "documents": documents, "count": list(count)[0][0]}


@allow("authenticated")
@schema("create_document.json")
def put():
    """create an document"""
    body = request.get_json()

    current_app.validate_user_schemas(body["document"])

    document = Document(namespace=body["document"]["namespace"])

    version = DocumentVersion(
        document=document,
        user=current_user,
        comment=body["comment"],
        data=json.dumps(body["document"]["data"]),
    )

    document.last_version = version
    document.associated_ids = current_app.get_associated_ids(version.as_dict())

    current_app.database.session.add(document)
    current_app.database.session.add(version)

    current_app.database.session.commit()

    document.clear_memory_cache()

    return {"status": "ok", "document": current_app.cook(version.as_dict())}
