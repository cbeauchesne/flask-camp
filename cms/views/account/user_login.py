""" Views related to account operations """

from flask import request, current_app
from flask_login import login_user, logout_user
from werkzeug.exceptions import Unauthorized

from cms.decorators import allow
from cms.models.user import User as UserModel
from cms.schemas import schema


rule = "/login"


@allow("anonymous")
@schema("cms/schemas/login_user.json")
def post():
    """Authentificate an user"""
    data = request.get_json()

    name = data["name"]
    password = data.get("password", None)
    token = data.get("token", None)

    user = UserModel.get(name=name)

    if user is None:
        raise Unauthorized(f"User [{name}] does not exists, or password is wrong")

    if not user.email_is_validated:
        raise Unauthorized("User's email is not validated")

    if user.check_auth(password=password, token=token):
        login_user(user)
    else:
        raise Unauthorized(f"User [{name}] does not exists, or password is wrong")

    current_app.database.session.commit()  # useless, but TODO : save last login date

    return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


@allow("blocked")
def delete():
    """Logout current user"""
    logout_user()

    return {"status": "ok"}
