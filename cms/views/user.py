import secrets

from flask import request
from flask_login import login_user, logout_user, login_required
from flask_restful import Resource
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized

from cms.models.user import User as UserModel


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
        user.update()

        return {"status": "ok"}


class UsersView(Resource):
    def get(self):
        # returns all user
        return {"status": "ok"}

    def put(self):
        """create an user"""
        data = request.get_json()

        password = data.pop("password")
        user = UserModel(**data)
        user.set_password(password)

        user.validation_token = secrets.token_hex(UserModel.password_hash.type.length)
        user.create()

        return {"status": "ok", "user": user.as_dict()}


class UserLoginView(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]

        user = UserModel.get(username=username)

        if user is None:
            print(f"User [{username}] doesn't exists")
            raise BadRequest("User does not exists, or password is wrong")

        if not user.check_password(password):
            raise BadRequest("User does not exists, or password is wrong")

        if user.validation_token is not None:
            raise Unauthorized("User is not validated")

        login_user(user)

        return {"status": "ok", "user": user.as_dict()}


class UserLogoutView(Resource):
    @login_required
    def get(self):
        logout_user()
        return {"status": "ok"}
