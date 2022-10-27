from flask import request
from flask_login import current_user
from werkzeug.exceptions import Forbidden, NotFound, BadRequest

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
def put(user_id):
    """Modify an user"""
    if user_id != current_user.id and not current_user.is_moderator and not current_user.is_admin:
        raise Forbidden("You can't modify this user")

    data = request.get_json()["user"]

    current_api.validate_user_schema(data)

    user = UserModel.get(id=user_id)

    if user is None:
        raise NotFound()

    password = data.get("password", None)
    token = data.get("token", None)

    if "name" in data:
        _update_name(user, data["name"])

    if "roles" in data:
        _update_roles(user, data["roles"])

    if "blocked" in data:
        _update_blocked(user, data["blocked"])

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

    current_api.on_user_update(user)

    # TODO : integrity error and test
    # TODO : on_user_update: old and new version
    current_api.database.session.commit()

    return {"status": "ok", "user": user.as_dict(include_personal_data=current_user.id == user.id)}


def _update_blocked(user, blocked):

    if blocked == user.blocked:
        return

    if not current_user.is_moderator:
        raise Forbidden("Only moderator can change names")

    user.blocked = blocked

    current_api.add_log(action="block" if blocked else "unblock", target_user=user)
    current_api.on_user_block(user)


def _update_name(user, name):
    name = UserModel.sanitize_name(name)

    if name == user.name:
        return

    if not current_user.is_moderator:
        raise Forbidden("Only moderator can change names")

    user.name = name

    current_api.add_log(action="Rename user", target_user=user)


def _update_roles(user, roles):
    roles = sorted(roles)

    if roles == sorted(user.roles):
        return

    if not current_user.is_admin:
        raise Forbidden("Only admin can change roles")

    for new_role in roles:

        if new_role not in current_api.user_roles:
            raise BadRequest(f"'{new_role}' doesn't exists. Possible roles are {sorted(current_api.user_roles)}.")

        if new_role not in user.roles:
            current_api.add_log(action=f"add_role {new_role}", target_user=user)

    for old_role in user.roles:
        if old_role not in roles:
            current_api.add_log(action=f"remove_role {old_role}", target_user=user)

    user.roles = roles
