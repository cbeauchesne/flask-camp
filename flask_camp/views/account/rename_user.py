from flask import request
from werkzeug.exceptions import NotFound

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp.models._user import User
from flask_camp._services._security import allow

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

    current_api.add_log(action="Rename user", comment=data["comment"], target_user=user)
    current_api.database.session.commit()

    return {"status": "ok"}
