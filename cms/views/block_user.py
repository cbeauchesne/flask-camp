from flask import current_app
from werkzeug.exceptions import NotFound

from cms.decorators import allow
from cms.models.user import User as UserModel
from cms.models.log import add_log
from cms.schemas import schema

rule = "/block_user/<int:user_id>"


@allow("moderator")
@schema("cms/schemas/comment.json")
def put(user_id):
    """Block an user"""

    user = UserModel.get(id=user_id)

    if not user:
        raise NotFound()

    user.blocked = True

    add_log(action="block", target_user=user)

    current_app.database.session.commit()

    return {"status": "ok"}


@allow("moderator")
@schema("cms/schemas/comment.json")
def delete(user_id):
    """Unblock an user"""
    user = UserModel.get(id=user_id)

    if not user:
        raise NotFound()

    user.blocked = False

    add_log(action="unblock", target_user=user)

    current_app.database.session.commit()

    return {"status": "ok"}
