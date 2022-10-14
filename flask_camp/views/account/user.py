import json

from flask import request
from flask_login import current_user
from werkzeug.exceptions import Forbidden, NotFound

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp._services._security import allow
from flask_camp.models._user import User as UserModel


rule = "/user/<int:user_id>"


@allow("anonymous", "authenticated", allow_blocked=True)
def get(user_id):
    """Get an user"""
    user = UserModel.get(id=user_id)

    if user is None:
        raise NotFound()

    include_personal_data = False

    if current_user.is_authenticated:
        if user.id == current_user.id:
            include_personal_data = True
        elif current_user.is_admin:
            include_personal_data = True

    return {
        "status": "ok",
        "user": user.as_dict(include_personal_data=include_personal_data),
    }


@allow("authenticated", allow_blocked=True)
@schema("modify_user.json")
def post(user_id):
    """Modify an user"""
    if user_id != current_user.id:
        raise Forbidden("You can't modify this user")

    data = request.get_json()

    user = UserModel.get(id=user_id)

    password = data.get("password", None)
    token = data.get("token", None)

    if "new_password" in data or "email" in data:
        if not user.check_auth(password=password, token=token):
            raise Forbidden()

    if "new_password" in data:
        user.set_password(data["new_password"])

    if "email" in data:
        user.set_email(data["email"])
        user.send_email_change_mail()

    if "ui_preferences" in data:
        user.ui_preferences = data["ui_preferences"]

    current_api.database.session.commit()

    # personal data : user is current user, so always true
    return {"status": "ok", "user": user.as_dict(include_personal_data=True)}
