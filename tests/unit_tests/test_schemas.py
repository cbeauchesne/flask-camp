import pytest

from flask_camp import RestApi
from tests.unit_tests.utils import BaseTest


class Test_Schemas(BaseTest):
    def test_error(self):
        with pytest.raises(FileNotFoundError):
            RestApi(schemas_directory="tests/unit_tests/schemas/", document_schemas=["notfound.json"])

        with pytest.raises(FileNotFoundError):
            RestApi(schemas_directory="tests/not_the_dir/")

    def test_missing_tailing_slash(self, user):
        self.login_user(user)
        self.create_document(namespace="outing", data=None, expected_status=400)
        self.create_document(namespace="route", data=None, expected_status=200)
        self.create_document(namespace="outing", data={"value": "str", "rating": "6a"}, expected_status=200)

    def test_basic(self, user):

        invalid_data = (
            None,
            {},
            {"value": None},
            {"value": 12},
            {"value": "str"},
            {"value": "str", "rating": None},
            {"value": "str", "rating": 12},
            {"value": "str", "rating": "a6"},
        )

        self.login_user(user)

        for data in invalid_data:
            self.create_document(namespace="outing", data=data, expected_status=400)

        doc = self.create_document(
            namespace="outing",
            data={"value": "str", "rating": "6a"},
            expected_status=200,
        ).json["document"]

        for data in invalid_data:
            self.modify_document(doc, data=data, expected_status=400)

        self.modify_document(doc, data={"value": "str", "rating": "6b"}, expected_status=200)

        route = self.create_document(namespace="route", data=None, expected_status=200).json["document"]
        self.modify_document(route, data=12, expected_status=200)
