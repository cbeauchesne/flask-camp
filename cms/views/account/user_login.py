""" Views related to account operations """

from flask import request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound

from cms.decorators import allow
from cms.limiter import limiter
from cms.models.user import User as UserModel
from cms.schemas import schema


rule = "/login"


@limiter.limit("1/second;5/minute;10/hour")
@allow("anonymous")
@schema("cms/schemas/login_user.json")
def post():
    data = request.get_json()

    name = data["name"]
    password = data.get("password", None)
    login_token = data.get("token", None)

    user = UserModel.get(name=name)

    if user is None:
        raise Unauthorized(f"User [{name}] does not exists, or password is wrong")

    if not user.email_is_validated:
        raise Unauthorized("User's email is not validated")

    if user.check_password(password):
        login_user(user)
    elif user.check_login_token(login_token):
        login_user(user)
    else:
        raise Unauthorized(f"User [{name}] does not exists, or password is wrong")

    user.update()

    return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


@allow("blocked")
def delete():
    logout_user()

    return {"status": "ok"}
