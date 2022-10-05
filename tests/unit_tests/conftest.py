import logging
import sys

import pytest

from flask_camp.models.user import User

from tests.unit_tests.app import app as tested_app
from tests.unit_tests.utils import BaseTest


# clean previous uncleaned state
# TODO put this in pytest hook, and don't do it if it's only collect
with tested_app.app_context():
    tested_app.database.drop_all()

tested_app.memory_cache.flushall()


def pytest_configure(config):
    if config.getoption("-v") > 1:
        logging.getLogger("sqlalchemy").addHandler(logging.StreamHandler(sys.stdout))
        logging.getLogger("sqlalchemy").setLevel(logging.INFO)


@pytest.fixture(autouse=True)
def setup_app():

    with tested_app.app_context():
        tested_app.init_databases()

    with tested_app.test_client() as client:
        BaseTest.client = client
        yield

    with tested_app.app_context():
        tested_app.database.drop_all()

    tested_app.memory_cache.flushall()


def _db_add_user(name="name", email=None, password="password", validate_email=True, roles=""):
    with tested_app.app_context():
        instance = User(
            name=name,
            roles=roles
            if isinstance(roles, (list, tuple))
            else [
                roles,
            ],
        )
        instance.set_password(password)

        instance.set_email(email if email else f"{name}@site.org")

        if validate_email:
            instance.validate_email(instance._email_token)

        tested_app.database.session.add(instance)
        tested_app.database.session.commit()

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
    with tested_app.app_context():
        instance = User.get(name="admin")
        yield User(
            id=instance.id,
            name=instance.name,
            _email=instance._email,
            _email_to_validate=instance._email_to_validate,
            _email_token=instance._email_token,
            roles=instance.roles,
        )


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


@pytest.fixture()
def database():
    yield tested_app.database


@pytest.fixture()
def mail():
    yield tested_app.mail._mail


@pytest.fixture()
def memory_cache():
    yield tested_app.memory_cache


@pytest.fixture()
def cant_send_mail():
    def raise_exception(*args, **kwargs):
        raise Exception("That was not expcted!")

    original_send = tested_app.mail._mail.send
    tested_app.mail._mail.send = raise_exception

    yield

    tested_app.mail._mail.send = original_send


@pytest.fixture()
def drop_all():
    with tested_app.app_context():
        tested_app.database.drop_all()

    tested_app.memory_cache.flushall()


@pytest.fixture()
def app():
    yield tested_app
