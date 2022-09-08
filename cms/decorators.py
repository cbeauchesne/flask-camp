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
