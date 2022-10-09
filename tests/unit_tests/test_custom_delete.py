import pytest
from werkzeug.exceptions import Forbidden

from flask_camp import RestApi
from flask_camp.exceptions import ConfigurationError
from tests.unit_tests.utils import create_test_app
from tests.unit_tests.utils import BaseTest


def before_document_delete(user, document_as_dict):
    """Stupid test: user cant delete if it's the last editor"""
    if document_as_dict["user"]["id"] == user.id:
        raise Forbidden()


class Test_CustomDelete(BaseTest):
    def test_error(self):
        with pytest.raises(ConfigurationError):
            RestApi(before_document_delete={})

    def test_main(self, user, user_2):
        app = create_test_app()
        RestApi(app=app, user_can_delete=True, before_document_delete=before_document_delete)

        with app.test_client() as base_client:
            BaseTest.client = base_client
            self.login_user(user)

            document = self.create_document().json["document"]

            self.delete_document(document, expected_status=403)

            self.login_user(user_2)
            self.delete_document(document, expected_status=200)

    def test_normal_conf(self, user, user_2):
        self.login_user(user)
        document = self.create_document().json["document"]
        self.delete_document(document, expected_status=403)

        self.login_user(user_2)
        self.delete_document(document, expected_status=403)