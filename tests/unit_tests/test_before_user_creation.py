import pytest
from werkzeug.exceptions import Forbidden

from flask import request
from flask_camp import RestApi
from flask_camp.models import Document, User
from flask_camp.exceptions import ConfigurationError

from tests.unit_tests.app import create_test_app
from tests.unit_tests.utils import BaseTest


def before_user_creation(user):
    """
    Two actions:
    1. user must provide a captcha
    2. a document is created, and user id is set to the document's id
    """

    data = request.get_json()
    if "captcha" not in data:
        raise Forbidden()

    admin_user = User.get(id=1)
    user_page = Document.create(
        comment="Automatic creation of user page",
        data=None,
        author=admin_user,
    )

    user.id = user_page.id


class Test_BeforeUserCreation(BaseTest):
    def test_error(self):
        with pytest.raises(ConfigurationError):
            RestApi(before_user_creation={})

    def test_main(self, admin):
        app = create_test_app()
        RestApi(app=app, before_user_creation=before_user_creation)

        client = BaseTest()

        with app.test_client() as base_client:
            client.client = base_client

            # first create some pages
            client.login_user(admin)
            client.create_document()
            client.create_document()
            client.create_document()

            # admin id = 1
            # page 1, 2 and 3 exists

            client.logout_user()

            client.create_user(expected_status=403)
            user = client.create_user(json={"captcha": 42}, expected_status=200).json["user"]

            client.get_document(4, expected_status=200)
            assert user["id"] == 4  # without before_user_creation, it would have been 2
