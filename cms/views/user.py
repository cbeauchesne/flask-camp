from flask import request
from flask_login import login_user, logout_user, login_required, current_user
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound

from cms import database
from cms.models.user import User as UserModel
from cms.schemas import schema


class UserValidationView(Resource):
    """validate the user with the validation token"""

    def get(self, user_id):
        user = UserModel.get(id=user_id)
        token = request.args["validation_token"]

        if user.validation_token is None:
            raise BadRequest("User is still validated")

        if token != user.validation_token:
            raise BadRequest("Token doesn't match")

        user.validation_token = None
        user.email = user.email_to_validate
        user.email_to_validate = None

        try:
            user.update()
        except IntegrityError as e:
            error_info = e.orig.args
            if error_info[0] == "UNIQUE constraint failed: user.email":
                raise BadRequest("A user still exists with this email")
            else:
                raise BadRequest(error_info[0])

        return {"status": "ok"}


class UsersView(Resource):
    @schema("cms/schemas/create_user.json")
    def put(self):
        """create an user"""
        data = request.get_json()

        if UserModel.get(email=data["email"]) is not None:
            # there is a race condition here, but it's kind of inevitable
            raise BadRequest("A user still exists with this email")

        user = UserModel(name=data["name"], email_to_validate=data["email"])
        user.set_password(data["password"])

        user.set_validation_token()
        # TODO send an email

        try:
            user.create()
        except IntegrityError as e:
            error_info = e.orig.args
            if error_info[0] == "UNIQUE constraint failed: user.name":
                raise BadRequest("A user still exists with this name")
            else:
                raise BadRequest(error_info[0])

        return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


class UserLoginView(Resource):
    @schema("cms/schemas/login_user.json")
    def post(self):
        data = request.get_json()

        name = data["name"]
        password = data["password"]

        user = UserModel.get(name=name)

        if user is None:
            print(f"User [{name}] doesn't exists")
            raise BadRequest("User does not exists, or password is wrong")

        if not user.check_password(password):
            print(f"Wrong password for user {user}")
            raise BadRequest("User does not exists, or password is wrong")

        if user.email is None:
            raise Unauthorized("User's email is not validated")

        login_user(user)

        return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


class UserLogoutView(Resource):
    @login_required
    def get(self):
        logout_user()

        return {"status": "ok"}


class UserView(Resource):
    def get(self, id):
        user = UserModel.get(id=id)

        if user is None:
            raise NotFound()

        return {
            "status": "ok",
            "user": user.as_dict(include_personal_data=id == current_user.id or current_user.is_admin),
        }

    @login_required
    @schema("cms/schemas/modify_user.json")
    def post(self, id):
        if id != current_user.id and not current_user.is_admin:
            raise Unauthorized("You can't modify this user")

        # TODO log if current_user.is_admin

        data = request.get_json()

        user = UserModel.get(id=id)

        if "password" in data:
            # TODO check current password
            print(f"Update {current_user}'s password")
            user.set_password(data["password"])

        if "email" in data:
            if user.get(email=data["email"]) is not None:
                raise BadRequest("A user still exists with this email")

            print(f"Update {current_user}'s email")
            user.email_to_validate = data["email"]
            user.set_validation_token()
            # TODO send an email

        if "roles" in data and current_user.is_admin:
            user.roles = ",".join(data["roles"])

        database.session.commit()

        # personal data : user is current user or admin, so always true
        return {"status": "ok", "user": user.as_dict(include_personal_data=True)}
