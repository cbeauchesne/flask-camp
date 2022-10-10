from flask import request
from werkzeug.exceptions import BadRequest, NotFound

from flask_camp.services.security import allow
from flask_camp.models.log import add_log
from flask_camp.models.user import User
from flask_camp.schemas import schema
from flask_camp.services.database import database
from flask_camp.utils import current_api

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

    add_log(action=f"add_role {role}", comment=data["comment"], target_user=user)

    database.session.commit()

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

    add_log(action=f"remove_role {role}", comment=data["comment"], target_user=user)

    database.session.commit()

    return {"status": "ok", "roles": user.roles}
