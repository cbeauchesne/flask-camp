from functools import wraps

from flask_login import current_user
from werkzeug.exceptions import Forbidden


def allow(*args, allow_blocked=False):
    """simple decorator that add roles attributes to a function"""

    allowed_roles = set(args)

    def decorator(f):

        setattr(f, "allowed_roles", allowed_roles)
        setattr(f, "allow_blocked", allow_blocked)

        return f

    return decorator


def check_rights(f):
    """Takes a function in argument, and return it decorated with a right checker
    The function must have been decorated woth the @allow decorator"""

    @wraps(f)
    def wrapper(*args, **kwargs):

        if current_user.blocked and not f.allow_blocked:
            raise Forbidden("You have been blocked, you can't access to this resource")

        user_roles = list(current_user.roles)

        if current_user.is_authenticated:
            user_roles.append("authenticated")

        for user_role in user_roles:
            if user_role in f.allowed_roles:
                return f(*args, **kwargs)

        raise Forbidden("You can't access to this resource")

    return wrapper
