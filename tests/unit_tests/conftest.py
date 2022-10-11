import logging
import sys

from flask import Flask
import pytest

from flask_camp import RestApi
from flask_camp.models import User


tested_app = Flask(__name__, static_folder=None)
tested_app.config.update({"TESTING": True, "SECRET_KEY": "not very secret", "SQLALCHEMY_TRACK_MODIFICATIONS": False})
tested_api = RestApi(app=tested_app)


logging.basicConfig(format="%(asctime)s [%(levelname)8s] %(message)s")


def pytest_configure(config):
    if config.getoption("-v") > 1:
        logging.getLogger("sqlalchemy").addHandler(logging.StreamHandler(sys.stdout))
        logging.getLogger("sqlalchemy").setLevel(logging.INFO)

    if not config.option.collectonly:
        # clean previous uncleaned state
        # do not perform this on collect, editors that automatically collect tests on file change
        # may break current test session
        with tested_app.app_context():
            tested_api.database.drop_all()
            tested_api.create_all()

        tested_api.memory_cache.flushall()


def _db_add_user(name="name", email=None, password="password", validate_email=True, roles=None):

    with tested_app.app_context():
        instance = User(
            name=name,
            roles=roles if isinstance(roles, (list, tuple)) else roles.split(",") if isinstance(roles, str) else [],
        )
        instance.set_password(password)

        instance.set_email(email if email else f"{name}@site.org")

        if validate_email:
            instance.validate_email(instance._email_token)

        tested_api.database.session.add(instance)
        tested_api.database.session.commit()

        result = User(
            id=instance.id,
            name=instance.name,
            _email=instance._email,
            _email_to_validate=instance._email_to_validate,
            _email_token=instance._email_token,
            roles=instance.roles,
        )

    return result


@pytest.fixture()
def admin():
    yield _db_add_user(name="admin", roles="admin")


@pytest.fixture()
def moderator():
    yield _db_add_user(name="moderator", roles="moderator")


@pytest.fixture()
def user():
    yield _db_add_user()


@pytest.fixture()
def unvalidated_user():
    yield _db_add_user(validate_email=False)


@pytest.fixture()
def user_2():
    yield _db_add_user("user_2")
