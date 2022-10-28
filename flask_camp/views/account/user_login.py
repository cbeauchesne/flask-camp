""" Views related to account operations """

from flask import request
from flask_login import login_user, logout_user
from werkzeug.exceptions import Unauthorized

from flask_camp._schemas import schema
from flask_camp._services._security import allow
from flask_camp.models._user import User


rule = "/user/login"


@allow("anonymous", "authenticated")
@schema("login_user.json")
def put():
    """Login an user"""
    data = request.get_json()

    name_or_email = data["name_or_email"].strip().lower()

    if "@" in name_or_email:
        user = User.get(_email=name_or_email)
    else:
        user = User.get(name=name_or_email)

    password = data.get("password", None)
    token = data.get("token", None)

    if user is None or not user.check_auth(password=password, token=token):
        raise Unauthorized("User does not exists, or password is wrong")

    if not user.email_is_validated:
        raise Unauthorized("User's email is not validated")

    login_user(user)

    return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


@allow("authenticated", allow_blocked=True)
def delete():
    """Logout current user"""
    logout_user()

    return {"status": "ok"}
