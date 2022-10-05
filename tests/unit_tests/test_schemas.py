import pytest

from tests.unit_tests.utils import BaseTest


class Test_Schemas(BaseTest):
    def test_error(self, app):
        with pytest.raises(FileNotFoundError):
            app.register_schemas("tests/unit_tests/schemas/", ["notfound.json"])

        with pytest.raises(FileNotFoundError):
            app.register_schemas("tests/not_the_dir/", ["notfound.json"])

    def test_missing_tailing_slash(self, user, app):
        app.register_schemas("tests/unit_tests/schemas", ["outing.json"])

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

        doc = self.create_document(namespace="outing", data={"value": "str", "rating": "6a"}, expected_status=200).json[
            "document"
        ]

        for data in invalid_data:
            self.modify_document(doc, data=data, expected_status=400)

        self.modify_document(doc, data={"value": "str", "rating": "6b"}, expected_status=200)

        route = self.create_document(namespace="route", data=None, expected_status=200).json["document"]
        self.modify_document(route, data=12, expected_status=200)
