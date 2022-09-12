from functools import wraps
import logging


from flask_login import current_user
from werkzeug.exceptions import Forbidden


log = logging.getLogger(__name__)


def allow_anonymous(func):
    setattr(func, "__allow_anonymous", True)

    return func


def allow_blocked(func):
    setattr(func, "__allow_blocked", True)

    return func


def allow_authenticated(func):
    setattr(func, "__allow_authenticated", True)

    return func


def allow_moderator(func):
    setattr(func, "__allow_moderator", True)

    return func


def allow(*args):

    items = set(args)

    for item in items:
        assert item in ["anonymous", "blocked", "authenticated", "moderator", "admin"], f"{item} is not recognised"

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            allowed = False

            if "anonymous" in items:
                allowed = True

            elif current_user.is_authenticated:

                if "blocked" in items:
                    allowed = True

                if not current_user.blocked:
                    if "authenticated" in items:
                        allowed = True
                    elif "moderator" in items and current_user.is_moderator:
                        allowed = True
                    elif "admin" in items and current_user.is_admin:
                        allowed = True

            if not allowed:
                raise Forbidden()

            return f(*args, **kwargs)

        return wrapper

    return decorator
