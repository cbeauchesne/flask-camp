from flask import request, current_app
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from cms.decorators import allow
from cms.models.user import User as UserModel
from cms.schemas import schema

rule = "/users"


@allow("anonymous")
@schema("cms/schemas/create_user.json")
def put():
    """create an user"""

    if current_user.is_authenticated:
        raise BadRequest()

    data = request.get_json()

    user = UserModel(name=data["name"])
    user.set_password(data["password"])
    user.set_email(data["email"])

    current_app.database.session.add(user)

    try:
        current_app.database.session.commit()
    except IntegrityError as e:
        error_info = e.orig.args
        if error_info[0] == "UNIQUE constraint failed: user.name":
            raise BadRequest("A user still exists with this name") from e
        else:
            raise BadRequest(error_info[0]) from e

    user.send_account_creation_mail()

    return {"status": "ok", "user": user.as_dict()}
