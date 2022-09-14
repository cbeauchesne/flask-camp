import pytest

from cms.application import Application
from cms.models.user import User

from tests.utils import BaseTest


@pytest.fixture(autouse=True)
def setup_app():

    app = Application(TESTING=True)

    app.add_url_rule("/__testing/500", view_func=lambda: 1 / 0, endpoint="500")
    app.add_url_rule("/__testing/vuln/<int:id>", view_func=lambda id: User.get(id=id).as_dict(True), endpoint="vuln")

    app.create_all()
    with app.test_client() as client:
        BaseTest.client = client
        yield
