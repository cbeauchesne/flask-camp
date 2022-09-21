import logging
import sys

import pytest

from fakeredis import FakeServer, FakeRedis

from cms import config as cms_config
from cms.application import Application
from cms.models.user import User

from tests.unit_tests.utils import BaseTest

redis_server = FakeServer()
redis_client = FakeRedis(server=redis_server)

app = Application(cms_config.Testing, memory_cache_instance=redis_client)

app.add_url_rule("/__testing/500", view_func=lambda: 1 / 0, endpoint="500")
app.add_url_rule("/__testing/vuln/<int:id>", view_func=lambda id: User.get(id=id).as_dict(True), endpoint="vuln")


def pytest_configure(config):
    if config.getoption("-v") > 1:
        logging.getLogger("sqlalchemy").addHandler(logging.StreamHandler(sys.stdout))
        logging.getLogger("sqlalchemy").setLevel(logging.INFO)


@pytest.fixture(autouse=True)
def setup_app():

    with app.app_context():
        app.create_all()

    with app.test_client() as client:
        BaseTest.client = client
        yield

    with app.app_context():
        app.database.drop_all()

    redis_client.flushall()


def db_add_user(name="name", email=None, password="password", validate_email=True, roles=""):
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
    yield db_add_user(name="admin", roles="admin")


@pytest.fixture()
def moderator():
    yield db_add_user(name="moderator", roles="moderator")


@pytest.fixture()
def user():
    yield db_add_user()


@pytest.fixture()
def unvalidated_user():
    yield db_add_user(validate_email=False)


@pytest.fixture()
def user_2():
    yield db_add_user("user_2")


@pytest.fixture()
def database():
    yield app.database


@pytest.fixture()
def mail():
    yield app.mail


@pytest.fixture()
def memory_cache():
    yield app.memory_cache
