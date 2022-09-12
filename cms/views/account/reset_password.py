""" Views related to account operations """

from flask import request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound

from cms import database
from cms.decorators import allow
from cms.models.user import User as UserModel
from cms.schemas import schema


rule = "/reset_password"


@allow("anonymous")
@schema("cms/schemas/reset_password.json")
def post():
    email = request.get_json()["email"]

    user = UserModel.get(_email=email)

    if user is None:  # do not let hacker crawl our base
        fake_user = UserModel()
        fake_user.set_login_token()

        return {"status": "ok", "expiration_date": fake_user.login_token_expiration_date.isoformat()}

    user.set_login_token()
    user.update()

    return {"status": "ok", "expiration_date": user.login_token_expiration_date.isoformat()}
