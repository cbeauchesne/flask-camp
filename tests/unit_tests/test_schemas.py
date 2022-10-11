import pytest

from flask_camp import RestApi
from tests.unit_tests.utils import BaseTest


class Test_Errors:
    def test_error(self):
        with pytest.raises(FileNotFoundError):
            RestApi(schemas_directory="tests/unit_tests/schemas/", document_schemas=["notfound.json"])

        with pytest.raises(FileNotFoundError):
            RestApi(schemas_directory="tests/not_the_dir/")


class Test_Schemas(BaseTest):
    rest_api_kwargs = {
        "schemas_directory": "tests/unit_tests/schemas",
        "document_schemas": ["outing.json"],
    }

    def test_basic(self, user):

        invalid_data = (
            {"namespace": "outing"},
            {"namespace": "outing", "value": None},
            {"namespace": "outing", "value": 12},
            {"namespace": "outing", "value": "str"},
            {"namespace": "outing", "value": "str", "rating": None},
            {"namespace": "outing", "value": "str", "rating": 12},
            {"namespace": "outing", "value": "str", "rating": "a6"},
        )

        self.login_user(user)

        for data in invalid_data:
            self.create_document(data=data, expected_status=400)

        doc = self.create_document(
            data={"namespace": "outing", "value": "str", "rating": "6a"},
            expected_status=200,
        ).json["document"]

        for data in invalid_data:
            self.modify_document(doc, data=data, expected_status=400)

        self.modify_document(doc, data={"namespace": "outing", "value": "str", "rating": "6b"}, expected_status=200)

        route = self.create_document(data={"namespace": "route"}, expected_status=200).json["document"]
        self.modify_document(route, data=12, expected_status=200)
