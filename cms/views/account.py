""" Views related to account operations """

from flask import request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound

from cms import database
from cms.decorators import allow_anonymous, allow_blocked, allow_authenticated
from cms.models.user import User as UserModel
from cms.schemas import schema
from cms.views.core import BaseResource


class UserLoginView(BaseResource):
    @allow_anonymous
    @schema("cms/schemas/login_user.json")
    def post(self):
        data = request.get_json()

        name = data["name"]
        password = data.get("password", None)
        login_token = data.get("token", None)

        user = UserModel.get(name=name)

        if user is None:
            print(f"User [{name}] doesn't exists")
            raise Unauthorized("User does not exists, or password is wrong")

        if not user.email_is_validated:
            print(f"User [{name}] di not validate its mail")
            raise Unauthorized("User's email is not validated")

        if user.check_password(password):
            login_user(user)
        elif user.check_login_token(login_token):
            login_user(user)
        else:
            print(f"Wrong auth for user {user}")
            raise Unauthorized("User does not exists, or password is wrong")

        user.update()

        return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


class UserLogoutView(BaseResource):
    @allow_blocked
    def get(self):
        logout_user()

        return {"status": "ok"}


class EmailValidationView(BaseResource):
    """validate the user email with the validation token"""

    @allow_anonymous
    @schema("cms/schemas/validate_email.json")
    def post(self):
        data = request.get_json()
        user = UserModel.get(name=data["name"])

        if user is None:
            raise NotFound()

        user.validate_email(data["token"])

        try:
            database.session.commit()
        except IntegrityError as e:
            error_info = e.orig.args
            if error_info[0] == "UNIQUE constraint failed: user.email":
                raise BadRequest("A user still exists with this email")
            else:
                raise BadRequest(error_info[0])

        return {"status": "ok"}


class ResetPasswordView(BaseResource):
    @allow_anonymous
    @schema("cms/schemas/reset_password.json")
    def post(self):
        email = request.get_json()["email"]

        user = UserModel.get(_email=email)

        if user is None:  # do not let hacker crawl our base
            fake_user = UserModel()
            fake_user.set_login_token()

            return {"status": "ok", "expiration_date": fake_user.login_token_expiration_date.isoformat()}

        user.set_login_token()
        user.update()

        return {"status": "ok", "expiration_date": user.login_token_expiration_date.isoformat()}
