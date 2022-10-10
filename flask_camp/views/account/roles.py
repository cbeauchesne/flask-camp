from flask import request
from werkzeug.exceptions import BadRequest, NotFound

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp.models._user import User
from flask_camp._services._security import allow

rule = "/roles/<int:user_id>"


@allow("anonymous", "authenticated")
def get(user_id):
    """Get roles for a given user"""

    user = User.get(id=user_id)

    if user is None:
        raise NotFound()

    return {"status": "ok", "roles": user.roles}


@allow("admin")
@schema("modify_role.json")
def post(user_id):
    """Add a role to an user"""
    user = User.get(id=user_id, with_for_update=True)

    if user is None:
        raise NotFound()

    data = request.get_json()

    role = data["role"]

    if role not in current_api.user_roles:
        raise BadRequest(f"'{role}' doesn't exists. Possible roles are {sorted(current_api.user_roles)}.")

    if role in user.roles:
        raise BadRequest("User has this role")

    user.roles = user.roles + [role]

    current_api.add_log(action=f"add_role {role}", comment=data["comment"], target_user=user)
    current_api.database.session.commit()

    return {"status": "ok", "roles": user.roles}


@allow("admin")
@schema("modify_role.json")
def delete(user_id):
    """Remove a role from an user"""
    user = User.get(id=user_id, with_for_update=True)

    if user is None:
        raise NotFound()

    data = request.get_json()

    role = data["role"]

    if role not in user.roles:
        raise BadRequest("User does not have this role")

    roles = list(user.roles)
    roles.remove(role)
    user.roles = roles

    current_api.add_log(action=f"remove_role {role}", comment=data["comment"], target_user=user)
    current_api.database.session.commit()

    return {"status": "ok", "roles": user.roles}
