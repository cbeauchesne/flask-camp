from functools import wraps
import logging

from flask_login import current_user
from werkzeug.exceptions import Forbidden


log = logging.getLogger(__name__)


def allow(*args, allow_blocked=False):

    allowed_roles = set(args)

    for role in allowed_roles:
        assert role in ["anonymous", "authenticated", "moderator", "admin"], f"{role} is not recognised"

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            if current_user.blocked and not allow_blocked:
                raise Forbidden("You have been blocked, you can't access to this resource")

            user_roles = current_user.roles

            if current_user.is_authenticated:
                user_roles.append("authenticated")

            for user_role in user_roles:
                if user_role in allowed_roles:
                    return f(*args, **kwargs)

            raise Forbidden("You can't access to this resource")

        return wrapper

    return decorator
