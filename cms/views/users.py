from flask import request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound

from cms import database
from cms.decorators import allow
from cms.models.user import User as UserModel
from cms.schemas import schema

rule = "/users"


@allow("anonymous")
@schema("cms/schemas/create_user.json")
def put():
    """create an user"""
    data = request.get_json()

    user = UserModel(name=data["name"])
    user.set_password(data["password"])
    user.set_email(data["email"])

    try:
        user.create()
    except IntegrityError as e:
        error_info = e.orig.args
        if error_info[0] == "UNIQUE constraint failed: user.name":
            raise BadRequest("A user still exists with this name")
        else:
            raise BadRequest(error_info[0])

    return {"status": "ok", "user": user.as_dict()}
