from flask import request
from flask_login import current_user
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound

from cms import database
from cms.decorators import allow
from cms.models.log import add_log
from cms.models.user_tag import UserTag
from cms.schemas import schema

rule = "/user_tags"


def _build_filters(**kwargs):
    return {k: v for key, value in kwargs.items() if value is not None}


@allow("blocked")
def get():

    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)

    filters = _build_filters(
        user_id=request.args.get("user_id", default=None, type=int),
        document_id=request.args.get("document_id", default=None, type=int),
        name=request.args.get("name", default=None, type=str),
        value=request.args.get("value", default=None, type=str),
    )

    query = UserTag.query()

    if len(filters) != 0:
        query = query.filter_by(**filters)

    count = query.count()
    query = query.offset(offset).limit(limit)

    return {
        "status": "ok",
        "count": count,
        "user_tags": [tag.as_dict() for tag in query],
    }


@allow("blocked")
@schema("cms/schemas/modify_user_tag.json")
def post():
    """create/modify an user tag"""
    data = request.get_json()

    document_id = data["document_id"]
    name = data["name"]
    value = data.get("value", None)

    tag = UserTag.get(name=name, document_id=document_id, user_id=current_user.id)
    if tag is None:
        tag = UserTag(name=name, document_id=document_id, user_id=current_user.id)
        database.session.add(tag)

    tag.value = value

    database.session.commit()

    return {"status": "ok", "user_tag": tag.as_dict()}


@allow("blocked")
@schema("cms/schemas/delete_user_tag.json")
def delete():
    data = request.get_json()

    document_id = data["document_id"]
    name = data["name"]

    tag = UserTag.get(name=name, document_id=document_id, user_id=current_user.id)

    if not tag:
        raise NotFound()

    database.session.delete(tag)
    database.session.commit()

    return {"status": "ok"}
