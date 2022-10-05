from flask import current_app, request
from werkzeug.exceptions import NotFound, BadRequest

from flask_camp.services.security import allow
from flask_camp.models.user import User as UserModel
from flask_camp.models.log import add_log
from flask_camp.schemas import schema

rule = "/block_user/<int:user_id>"


@allow("moderator")
@schema("action_with_comment.json")
def post(user_id):
    """Block/unblock an user"""

    user = UserModel.get(id=user_id, with_for_update=True)

    if not user:
        raise NotFound()

    blocked = request.get_json()["blocked"]

    if blocked == user.blocked:
        raise BadRequest("User is still blocked/unblocked")

    user.blocked = blocked

    add_log(action="block" if blocked else "unblock", target_user=user)

    current_app.database.session.commit()

    return {"status": "ok"}
