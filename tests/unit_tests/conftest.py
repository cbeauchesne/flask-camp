import logging
import sys

import pytest

from cms import config as cms_config
from cms.application import Application
from cms.models.user import User

from tests.unit_tests.utils import BaseTest

app = Application(cms_config.Testing)


@app.route("/__testing/500", methods=["GET"])
def testing_500():
    """This function will raise a 500 response"""
    return 1 / 0


@app.route("/__testing/vuln/<int:user_id>", methods=["GET"])
def testing_vuln(user_id):
    """Calling this method without being authentified as user_id mys raise a Forbidden response"""
    return User.get(id=user_id).as_dict(include_personal_data=True)


def pytest_configure(config):
    if config.getoption("-v") > 1:
        logging.getLogger("sqlalchemy").addHandler(logging.StreamHandler(sys.stdout))
        logging.getLogger("sqlalchemy").setLevel(logging.INFO)


@pytest.fixture(autouse=True)
def setup_app():

    with app.app_context():
        app.init_databases()

    with app.test_client() as client:
        BaseTest.client = client
        yield

    with app.app_context():
        app.database.drop_all()

    app.memory_cache.flushall()


def _db_add_user(name="name", email=None, password="password", validate_email=True, roles=""):
    with app.app_context():
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

        app.database.session.add(instance)
        app.database.session.commit()

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
    with app.app_context():
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
    yield app.database


@pytest.fixture()
def mail():
    yield app.mail


@pytest.fixture()
def memory_cache():
    yield app.memory_cache


@pytest.fixture()
def cant_send_mail():
    def raise_exception(*args, **kwargs):
        raise Exception("That was not expcted!")

    original_send = app.mail.send
    app.mail.send = raise_exception

    yield

    app.mail.send = original_send


@pytest.fixture()
def drop_all():
    with app.app_context():
        app.database.drop_all()

    app.memory_cache.flushall()
