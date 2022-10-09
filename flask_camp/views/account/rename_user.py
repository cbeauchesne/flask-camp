from flask import request
from werkzeug.exceptions import NotFound

from flask_camp.services.security import allow
from flask_camp.models.log import add_log
from flask_camp.models.user import User
from flask_camp.schemas import schema
from flask_camp.services.database import database

rule = "/rename_user/<int:user_id>"


@allow("moderator")
@schema("rename_user.json")
def post(user_id):
    """rename an user"""

    user = User.get(id=user_id, with_for_update=True)

    if user is None:
        raise NotFound()

    data = request.get_json()
    user.name = data["name"]

    database.session.commit()

    add_log(action="Rename user", comment=data["comment"], target_user=user)

    return {"status": "ok"}
