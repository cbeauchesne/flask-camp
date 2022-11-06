import re

import pytest

from flask_camp import RestApi, SchemaValidator
from flask_camp.exceptions import ConfigurationError
from tests.unit_tests.utils import BaseTest


def test_error():

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
        RestApi(user_schema=["outing.json"])
    assert e.match("You provide user_schema wihtout schemas_directory")

    with pytest.raises(ValueError) as e:
        SchemaValidator("tests/unit_tests/schemas_with_error")
    assert e.match("JSON syntax error in tests/unit_tests/schemas_with_error/outing.json")


class Test_Schemas(BaseTest):
    rest_api_kwargs = {
        "schemas_directory": "tests/unit_tests/schemas",
        "user_schema": "user.json",
    }

    def test_basic_user(self):
        invalid_data = (None, 12, {}, {"lang": 12}, {"lang": "sp"})

        for item in invalid_data:
            self.create_user(data=item, expected_status=400)

        with self.api.mail.record_messages() as outbox:
            user = self.create_user(data={"lang": "fr"}, expected_status=200).json["user"]
            self.validate_email(user, token=re.sub(r"^(.*email_token=)", "", outbox[0].body))

        self.login_user(user)

        for item in invalid_data:
            self.modify_user(user, data=item, expected_status=400)

        self.modify_user(user=user, data={"lang": "de"}, expected_status=200)
