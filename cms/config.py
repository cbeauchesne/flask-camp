# pylint: disable=too-few-public-methods


class _BaseConfig:
    TESTING = False


class Production(_BaseConfig):
    DATABASE_URI = "mysql://user@localhost/foo"
    # SECRET_KEY must be set in FLASK_SECRET_KEY env var


class Development(_BaseConfig):
    DATABASE_URI = "sqlite:////sqlite.db"
    SECRET_KEY = "not_very_secret"


class Testing(_BaseConfig):
    DATABASE_URI = "sqlite://"
    TESTING = True
    RATELIMIT_ENABLED = False
    SECRET_KEY = "not_very_secret"
