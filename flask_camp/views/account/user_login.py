""" Views related to account operations """

from flask import request
from flask_login import login_user, logout_user
from werkzeug.exceptions import Unauthorized

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp._services._security import allow
from flask_camp.models._user import User as UserModel


rule = "/login"


@allow("anonymous", "authenticated")
@schema("login_user.json")
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

    current_api.database.session.commit()

    return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


@allow("authenticated", allow_blocked=True)
def delete():
    """Logout current user"""
    logout_user()

    return {"status": "ok"}
