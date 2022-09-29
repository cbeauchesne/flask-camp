from flask import current_app, request
from werkzeug.exceptions import NotFound, BadRequest

from cms.decorators import allow
from cms.models.user import User as UserModel
from cms.models.log import add_log
from cms.schemas import schema

rule = "/block_user/<int:user_id>"


@allow("moderator")
@schema("cms/schemas/comment.json")
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
