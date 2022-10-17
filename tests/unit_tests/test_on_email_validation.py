import re

from tests.unit_tests.utils import BaseTest


def on_email_validation(user):
    user.ui_preferences = "custom"


class Test_UserCreation(BaseTest):
    rest_api_kwargs = {"on_email_validation": on_email_validation}

    def test_main(self):
        name, email, password = "my_user", "a@b.c", "week password"

        with self.api.mail.record_messages() as outbox:
            user = self.create_user(name, email, password).json["user"]
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        self.validate_email(user=user, token=token)
        user = self.get_user(user).json["user"]
        assert user["ui_preferences"] == "custom"
