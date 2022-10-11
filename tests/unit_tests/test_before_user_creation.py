import pytest
from werkzeug.exceptions import Forbidden

from flask import request
from flask_camp import RestApi
from flask_camp.models import Document, User
from flask_camp.exceptions import ConfigurationError

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


class Test_Error:
    def test_error(self):
        with pytest.raises(ConfigurationError):
            RestApi(before_user_creation={})


class Test_BeforeUserCreation(BaseTest):
    rest_api_kwargs = {"before_user_creation": before_user_creation}

    def test_main(self, admin):

        # first create some pages
        self.login_user(admin)
        self.create_document()
        self.create_document()
        self.create_document()

        # admin id = 1
        # page 1, 2 and 3 exists

        self.logout_user()

        self.create_user(expected_status=403)
        user = self.create_user(json={"captcha": 42}, expected_status=200).json["user"]

        self.get_document(4, expected_status=200)
        assert user["id"] == 4  # without before_user_creation, it would have been 2
