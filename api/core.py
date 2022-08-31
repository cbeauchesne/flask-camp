from flask import Flask

from .views.user import User as UserView, UserCreation, UserValidation, UserLogin, UserLogout

from .models.profile import Profile
from .models.user import User

from cms import database, Application


def create_app(**kwargs):
    app = Application(user_model=User)

    app.config.from_object(kwargs)

    app.add_resource(UserView, "/users/<int:user_id>")
    app.add_resource(UserCreation, "/create_user")
    app.add_resource(UserValidation, "/validate_user/<int:user_id>")
    app.add_resource(UserLogin, "/login")
    app.add_resource(UserLogout, "/logout")

    return app
