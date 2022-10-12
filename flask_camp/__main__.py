"""
flask_camp, Utils for flask_camp extension

Usage:
    flask_camp dev_env
    flask_camp init_db
    flask_camp add_admin <name> <email> <password>

Commands:
    dev_env     Start dev env, simply a redis on 6379 and a postgresql on 5432
    init_db     Init table in database
    add_admin   Adds an user with admin role
"""

import os
import subprocess

from flask import Flask
from docopt import docopt

from flask_camp import RestApi
from flask_camp.models import User


def _create_api():
    app = Flask(__name__)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAIL_DEFAULT_SENDER"] = app.config.get("MAIL_DEFAULT_SENDER", "do-not-reply@example.com")
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get(
        "SQLALCHEMY_DATABASE_URI", "postgresql://flask_camp_user:flask_camp_user@localhost:5432/flask_camp"
    )

    app.config.from_prefixed_env()
    api = RestApi(app)

    return app, api


def main(args):

    if args["dev_env"]:  # pragma: no cover
        docker_file = os.path.join(os.path.dirname(__file__), "docker-compose.yml")
        subprocess.run(
            ["docker", "compose", "-f", docker_file, "up", "--remove-orphans", "--wait", "-d", "redis", "pg"],
            check=True,
        )

    elif args["init_db"]:
        app, api = _create_api()

        with app.app_context():
            api.database.create_all()

    elif args["add_admin"]:
        app, api = _create_api()

        with app.app_context():
            user = User(name=args["<name>"], roles=["admin"])
            user.set_password(args["<password>"])
            user.set_email(args["<email>"])
            user.validate_email(user._email_token)
            api.database.session.add(user)
            api.database.session.commit()

            print(f"{user} is created")


def main_entry_point():  # pragma: no cover
    main(docopt(__doc__))


if __name__ == "__main__":  # pragma: no cover
    main_entry_point()
