from flask import request
from flask_login import login_user, logout_user, login_required, current_user
from flask_restful import Resource
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized

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
        user.update()

        return {"status": "ok"}


class UsersView(Resource):
    def get(self):
        # returns all user
        return {"status": "ok"}

    @schema("cms/schemas/create_user.json")
    def put(self):
        """create an user"""
        data = request.get_json()

        user = UserModel(username=data["username"], email_to_validate=data["email"])
        user.set_password(data["password"])

        user.set_validation_token()
        # TODO send an email

        user.create()

        return {"status": "ok", "user": user.as_dict(include_personal_data=True)}


class UserLoginView(Resource):
    @schema("cms/schemas/login_user.json")
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]

        user = UserModel.get(username=username)

        if user is None:
            print(f"User [{username}] doesn't exists")
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
    @login_required
    @schema("cms/schemas/modify_user.json")
    def post(self, id):
        if id != current_user.id:
            raise Unauthorized("You can't modify this user")

        data = request.get_json()
        if "password" in data:
            print(f"Update {current_user}'s password")
            current_user.set_password(data["password"])

        if "email" in data:
            print(f"Update {current_user}'s email")
            current_user.email_to_validate = data["email"]
            current_user.set_validation_token()
            # TODO send an email

        database.session.commit()

        return {"status": "ok"}
