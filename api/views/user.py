import secrets
from sqlalchemy.orm import Query

from werkzeug.exceptions import BadRequest, Forbidden
from flask import request
from flask_restful import Resource
from flask_login import login_user, logout_user, login_required

from api.models.user import User as UserModel


class User(Resource):
    @login_required
    def get(self):
        # returns an user model
        return {"status": "ok"}

    def post(self):
        # modify an user
        pass

    def delete(self):
        # delete an user
        pass


class UserValidation(Resource):
    def get(self, user_id):
        """validate the user with the validation token"""
        user = UserModel.get(id=user_id)
        token = request.args["validation_token"]

        if user.validation_token is None:
            raise BadRequest("User is still validated")

        if token != user.validation_token:
            raise BadRequest("Token doesn't match")

        user.validation_token = None
        user.update()

        return {"status": "ok"}


class UserCreation(Resource):
    def put(self):
        """create an user"""
        data = request.get_json()

        password = data.pop("password")
        user = UserModel(**data)
        user.set_password(password)

        user.validation_token = secrets.token_hex(UserModel.password_hash.type.length)
        user.create()

        return {"status": "ok", "user": user.as_dict()}


class Users(Resource):
    def get(self):
        # returns all user
        return {"status": "ok"}


class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user_id = data["user_id"]
        password = data["password"]

        user = UserModel.get(id=user_id)

        if user.validation_token is not None:
            raise Forbidden("User is not validated")

        if not user.check_password(password):
            raise Forbidden()

        login_user(user)

        return {"status": "ok", "user": user.as_dict()}


class UserLogout(Resource):
    def get(self):
        logout_user()

        return {"status": "ok"}
