import pytest

from api.core import create_app


@pytest.fixture
def client():
    app = create_app(TESTING=True)
    app.create_all()

    with app.test_client() as client:
        yield client
