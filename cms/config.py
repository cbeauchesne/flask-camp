# pylint: disable=too-few-public-methods


class _BaseConfig:
    TESTING = False


class Production(_BaseConfig):
    # DATABASE_URI must be in FLASK_DATABASE_URI env var
    # SECRET_KEY must be set in FLASK_SECRET_KEY env var
    # MAIL_DEFAULT_SENDER must be set in FLASK_MAIL_DEFAULT_SENDER env var

    RATELIMIT_STORAGE_URL = "memory://"  # TODO


class Development(_BaseConfig):
    DATABASE_URI = "sqlite:///sqlite.db"
    SECRET_KEY = "not_very_secret"

    RATELIMIT_STORAGE_URL = "memory://"

    MAIL_DEFAULT_SENDER = "do-not-reply@example.com"


class Testing(_BaseConfig):
    TESTING = True

    DATABASE_URI = "sqlite://"
    SECRET_KEY = "not_very_secret"

    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URL = "memory://"

    MAIL_DEFAULT_SENDER = "do-not-reply@example.com"
