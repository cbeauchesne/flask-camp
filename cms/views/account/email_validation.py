"""validate the user email with the validation token"""

from flask import request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound

from cms import database
from cms.decorators import allow
from cms.limiter import limiter
from cms.models.user import User as UserModel
from cms.schemas import schema

rule = "/validate_email"


@limiter.limit("10/hour")
@allow("anonymous")
@schema("cms/schemas/validate_email.json")
def post():
    data = request.get_json()
    user = UserModel.get(name=data["name"])

    if user is None:
        raise NotFound()

    user.validate_email(data["token"])

    try:
        database.session.commit()
    except IntegrityError as e:
        error_info = e.orig.args
        if error_info[0] == "UNIQUE constraint failed: user.email":
            raise BadRequest("A user still exists with this email")
        else:
            raise BadRequest(error_info[0])

    return {"status": "ok"}
