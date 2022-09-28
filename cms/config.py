# pylint: disable=too-few-public-methods


class _BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Production(_BaseConfig):
    ## Mandatory conf in environment variables:
    # FLASK_SECRET_KEY

    ## It'll work, but you may want to configure it:
    # FLASK_SQLALCHEMY_DATABASE_URI (default: memory)
    # FLASK_REDIS_HOST (default: memory)
    # FLASK_MAIL_DEFAULT_SENDER (default: do-not-reply@example.com)

    ## Optional but common configuration:
    # FLASK_RATELIMIT_DEFAULT. Exemple : "20000 per day,2000 per hour,300 per minute,10 per second"
    # FLASK_REDIS_PORT. If it's not 6379

    pass


class Development(_BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///sqlite.db"
    SECRET_KEY = "not_very_secret"

    MAIL_DEFAULT_SENDER = "do-not-reply@example.com"

    ERRORS_LOG_FILE = "logs/testing_errors.log"


class Testing(Development):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = None

    MAIL_DEFAULT_SENDER = None

    INIT_DATABASES = "True"

    RATELIMIT_ENABLED = False
