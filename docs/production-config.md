
    ## Mandatory conf in environment variables:
    # FLASK_SECRET_KEY

    ## It'll work, but you may want to configure it:
    # FLASK_SQLALCHEMY_DATABASE_URI (default: postgresql://flask_camp_user:flask_camp_user@localhost:5432/flask_camp)
    # FLASK_REDIS_HOST (default: localhost)
    # FLASK_REDIS_PORT (default: 6379)
    # FLASK_MAIL_DEFAULT_SENDER (default: do-not-reply@example.com)

    ## Optional but common configuration:
    # FLASK_RATELIMIT_DEFAULT. Exemple : "20000 per day,2000 per hour,300 per minute,10 per second"