import re

import pytest

from flask_camp import RestApi, SchemaValidator
from flask_camp.exceptions import ConfigurationError
from tests.unit_tests.utils import BaseTest


def test_error():
    # document schema does not exists
    with pytest.raises(FileNotFoundError) as e:
        RestApi(schemas_directory="tests/unit_tests/schemas/", document_schemas=["notfound.json"])
    assert e.match("File tests/unit_tests/schemas/notfound.json does not exists")

    # user schema does not exists
    with pytest.raises(FileNotFoundError) as e:
        RestApi(schemas_directory="tests/unit_tests/schemas/", user_schema="notfound.json")
    assert e.match("File tests/unit_tests/schemas/notfound.json does not exists")

    # schemas_directory does not exists
    with pytest.raises(FileNotFoundError) as e:
        RestApi(schemas_directory="tests/not_a_dir/")
    assert e.match("tests/not_a_dir/ is not a directory")

    # do not provide schemas_directory
    with pytest.raises(ConfigurationError) as e:
        RestApi(document_schemas=["outing.json"])
    assert e.match("You provide document_schemas wihtout schemas_directory")

    # do not provide schemas_directory
    with pytest.raises(ConfigurationError) as e:
        RestApi(user_schema=["outing.json"])
    assert e.match("You provide user_schema wihtout schemas_directory")

    with pytest.raises(ValueError) as e:
        SchemaValidator("tests/unit_tests/schemas_with_error")
    assert e.match("JSON syntax error in tests/unit_tests/schemas_with_error/outing.json")


class Test_Schemas(BaseTest):
    rest_api_kwargs = {
        "schemas_directory": "tests/unit_tests/schemas",
        "document_schemas": ["outing.json"],
        "user_schema": "user.json",
    }

    def test_basic_document(self, user):

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

    def test_basic_user(self):
        invalid_data = (None, 12, {}, {"lang": 12}, {"lang": "sp"})

        for item in invalid_data:
            self.create_user(ui_preferences=item, expected_status=400)

        with self.api.mail.record_messages() as outbox:
            user = self.create_user(ui_preferences={"lang": "fr"}, expected_status=200).json["user"]
            self.validate_email(user, token=re.sub(r"^(.*email_token=)", "", outbox[0].body))

        self.login_user(user)

        for item in invalid_data:
            self.modify_user(user, ui_preferences=item, expected_status=400)

        self.modify_user(user=user, ui_preferences={"lang": "de"}, expected_status=200)
