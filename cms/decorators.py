from functools import wraps

from flask_login import current_user
from werkzeug.exceptions import Forbidden


def moderator_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):

        if not current_user.is_authenticated:
            raise Forbidden("User is not logged in")

        if not current_user.is_moderator:
            raise Forbidden("User is not a moderator")

        return func(*args, **kwargs)

    return decorated_view


def user_must_not_be_blocked(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):

        if not current_user.is_authenticated:
            raise Forbidden("User is not logged in")

        if current_user.blocked:
            raise Forbidden("User is blocked")

        return func(*args, **kwargs)

    return decorated_view


# def admin_required(func):
#     @wraps(func)
#     def decorated_view(*args, **kwargs):
#         if not current_user.is_admin:
#             return current_app.login_manager.unauthorized()

#         return func(*args, **kwargs)

#     return decorated_view
