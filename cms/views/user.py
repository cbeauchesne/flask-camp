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


class UsersView(BaseResource):
    @allow_anonymous
    @schema("cms/schemas/create_user.json")
    def put(self):
        """create an user"""
        data = request.get_json()

        user = UserModel(name=data["name"])
        user.set_password(data["password"])
        user.set_email(data["email"])

        try:
            user.create()
        except IntegrityError as e:
            error_info = e.orig.args
            if error_info[0] == "UNIQUE constraint failed: user.name":
                raise BadRequest("A user still exists with this name")
            else:
                raise BadRequest(error_info[0])

        return {"status": "ok", "user": user.as_dict()}


class UserView(BaseResource):
    @allow_anonymous
    def get(self, id):
        user = UserModel.get(id=id)

        if user is None:
            raise NotFound()

        include_personal_data = False

        if current_user.is_authenticated:
            if user.id == current_user.id:
                include_personal_data = True
            elif current_user.is_admin:
                include_personal_data = True

        return {
            "status": "ok",
            "user": user.as_dict(include_personal_data=include_personal_data),
        }

    @allow_blocked
    @schema("cms/schemas/modify_user.json")
    def post(self, id):
        if id != current_user.id and not current_user.is_admin:
            raise Forbidden("You can't modify this user")

        # TODO log if current_user.is_admin

        data = request.get_json()

        user = UserModel.get(id=id)

        if "password" in data:
            # TODO check current password
            print(f"Update {current_user}'s password")
            user.set_password(data["password"])

        if "email" in data:
            user.set_email(data["email"])

        if "roles" in data and current_user.is_admin:
            user.roles = ",".join(data["roles"])

        database.session.commit()

        # personal data : user is current user or admin, so always true
        return {"status": "ok", "user": user.as_dict(include_personal_data=True)}
