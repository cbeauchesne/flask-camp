""" Views related to account operations """

from flask import request
from flask_login import login_user, logout_user
from werkzeug.exceptions import Unauthorized

from flask_camp._schemas import schema
from flask_camp._services._security import allow
from flask_camp.models._user import User


rule = "/login"


@allow("anonymous", "authenticated")
@schema("login_user.json")
def post():
    """Authentificate an user"""
    data = request.get_json()

    name = data["name"]
    password = data.get("password", None)
    token = data.get("token", None)

    user = User.get(name=name)

    if user is None or not user.check_auth(password=password, token=token):
        raise Unauthorized(f"User [{name}] does not exists, or password is wrong")

    if not user.email_is_validated:
        raise Unauthorized("User's email is not validated")

    login_user(user)

    return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


@allow("authenticated", allow_blocked=True)
def delete():
    """Logout current user"""
    logout_user()

    return {"status": "ok"}
