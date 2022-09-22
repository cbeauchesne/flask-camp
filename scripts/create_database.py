#!/usr/bin/env python3

if __name__ == "__main__":
    import logging
    import sys
    from cms import config
    from cms.application import Application
    from cms.models.user import User

    app = Application(config.Development)

    logging.getLogger("sqlalchemy").addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger("sqlalchemy").setLevel(logging.INFO)

    with app.app_context():
        app.create_all()

    user = User(
        name="admin",
        roles=[
            "admin",
        ],
    )
    with app.app_context():
        user.set_password("password")
        user.set_email("admin@example.com")
        user.validate_email(user._email_token)

        app.database.session.add(user)
        app.database.session.commit()
