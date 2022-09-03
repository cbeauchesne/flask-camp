import pytest

from cms.application import Application


@pytest.fixture
def client():
    app = Application(TESTING=True, sql_echo=True)
    app.create_all()

    with app.test_client() as client:
        yield client
