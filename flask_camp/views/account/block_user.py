from flask import request
from werkzeug.exceptions import NotFound, BadRequest

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp.models._user import User as UserModel
from flask_camp._services._security import allow

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

    current_api.add_log(action="block" if blocked else "unblock", target_user=user)
    current_api.database.session.commit()

    return {"status": "ok"}
