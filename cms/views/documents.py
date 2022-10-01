import json

from flask import request, current_app, Response
from flask_login import current_user
from werkzeug.exceptions import BadRequest

from cms.decorators import allow
from cms.limiter import limiter
from cms.models.document import Document, DocumentVersion
from cms.schemas import schema

rule = "/documents"


@allow("anonymous")
def get():
    """Get a list of documents"""

    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    return Response(
        response=current_app.memory_cache.search(limit=limit, offset=offset),
        content_type="application/json",
    )


@limiter.limit("1/second;10/minute;60/hour")
@allow("authenticated")
@schema("cms/schemas/create_document.json")
def put():
    """create an document"""
    body = request.get_json()

    comment = body.get("comment", "creation")
    namespace = body["document"]["namespace"]
    data = body["document"]["data"]

    document = Document(namespace=namespace)

    version = DocumentVersion(document=document, user=current_user, comment=comment, data=json.dumps(data))

    document.last_version = version

    current_app.database.session.add(document)
    current_app.database.session.add(version)

    current_app.database.session.commit()

    current_app.refresh_memory_cache(document.id)

    return {"status": "ok", "document": current_app.cook(version.as_dict())}
