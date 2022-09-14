from werkzeug.exceptions import NotFound

from cms import database
from cms.decorators import allow
from cms.models.user import User as UserModel
from cms.models.log import add_log
from cms.schemas import schema

rule = "/block_user/<int:id>"


@allow("moderator")
@schema("cms/schemas/comment.json")
def put(id):

    user = UserModel.get(id=id)

    if not user:
        raise NotFound()

    user.blocked = True

    add_log(action="block", target_user_id=id)

    database.session.commit()

    return {"status": "ok"}


@allow("moderator")
@schema("cms/schemas/comment.json")
def delete(id):
    user = UserModel.get(id=id)

    if not user:
        raise NotFound()

    user.blocked = False

    add_log(action="unblock", target_user_id=id)

    database.session.commit()

    return {"status": "ok"}
