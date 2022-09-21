# pylint: disable=too-few-public-methods


class _BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Production(_BaseConfig):
    # SQLALCHEMY_DATABASE_URI must be in FLASK_SQLALCHEMY_DATABASE_URI env var
    # SECRET_KEY must be set in FLASK_SECRET_KEY env var
    # MAIL_DEFAULT_SENDER must be set in FLASK_MAIL_DEFAULT_SENDER env var

    RATELIMIT_STORAGE_URI = "redis://redis:6379"


class Development(_BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///sqlite.db"
    SECRET_KEY = "not_very_secret"

    RATELIMIT_STORAGE_URI = "memory://"

    MAIL_DEFAULT_SENDER = "do-not-reply@example.com"


class Testing(_BaseConfig):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = "not_very_secret"

    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URI = "memory://"

    MAIL_DEFAULT_SENDER = "do-not-reply@example.com"

    INIT_DATABASE = "True"
