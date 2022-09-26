from flask import request, current_app
from flask_login import current_user
from werkzeug.exceptions import Forbidden, NotFound

from cms.decorators import allow
from cms.models.log import add_log
from cms.models.user import User as UserModel
from cms.schemas import schema


rule = "/user/<int:user_id>"


@allow("anonymous")
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


@allow("blocked")
@schema("cms/schemas/modify_user.json")
def post(user_id):
    """Modify an user"""
    if user_id != current_user.id and not current_user.is_admin:
        raise Forbidden("You can't modify this user")

    if current_user.is_admin and user_id != current_user.id:
        # if an admin modify an user, log actions
        log_admin_action = add_log
    else:
        # otherwise, do nothing
        def log_admin_action(**kwargs):  # pylint: disable=unused-argument
            pass

    data = request.get_json()

    user = UserModel.get(id=user_id)

    if "password" in data:
        # TODO check current password
        user.set_password(data["password"])
        log_admin_action(action="change_password", comment="", target_user_id=user.id)

    if "email" in data:
        user.set_email(data["email"])
        log_admin_action(action="change_email", comment="", target_user_id=user.id)
        user.send_email_change_mail()

    if "roles" in data and current_user.is_admin:
        new_roles = data["roles"]
        old_roles = user.roles

        user.roles = new_roles

        for role in old_roles:
            if not role in new_roles:
                log_admin_action(action=f"remove_role {role}", comment="", target_user_id=user.id)

        for role in new_roles:
            if not role in old_roles:
                log_admin_action(action=f"add_role {role}", comment="", target_user_id=user.id)

    current_app.database.session.commit()

    # personal data : user is current user or admin, so always true
    return {"status": "ok", "user": user.as_dict(include_personal_data=True)}
