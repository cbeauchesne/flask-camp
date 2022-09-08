from functools import wraps

from flask_login import current_user
from flask_restful import Resource
from werkzeug.exceptions import Forbidden


def check_rights(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        allow = False

        if hasattr(f, "__allow_anonymous"):
            allow = True

        elif current_user.is_authenticated:

            if hasattr(f, "__allow_blocked"):
                allow = True

            if not current_user.blocked:
                if hasattr(f, "__allow_authenticated"):
                    allow = True
                elif hasattr(f, "__allow_moderator") and current_user.is_moderator:
                    allow = True
                elif hasattr(f, "__allow_admin") and current_user.is_admin:
                    allow = True

        if not allow:
            raise Forbidden()

        return f(*args, **kwargs)

    return wrapper


class BaseResource(Resource):
    method_decorators = [check_rights]
