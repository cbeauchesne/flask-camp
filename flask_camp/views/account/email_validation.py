"""validate the user email with the validation token"""

from flask import request
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, NotFound

from flask_camp._schemas import schema
from flask_camp._utils import current_api
from flask_camp._services._security import allow
from flask_camp.models._user import User as UserModel

rule = "/validate_email"


@allow("admin")
def get():
    """Resend validation mail to a user. Only admin can do this request"""
    name = request.args.get("name", "")

    if not name:
        raise BadRequest()

    user = UserModel.get(name=name)
    if not user:
        raise NotFound()

    user.send_account_creation_mail()

    return {"status": "ok"}


@allow("anonymous", "authenticated")
@schema("validate_email.json")
def post():
    """Validate an email"""
    data = request.get_json()
    user = UserModel.get(name=data["name"])

    if user is None:
        raise NotFound()

    user.validate_email(data["token"])

    try:
        current_api.database.session.commit()
    except IntegrityError as e:
        raise BadRequest("A user still exists with this email") from e

    return {"status": "ok"}
