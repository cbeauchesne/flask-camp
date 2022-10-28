import re

from tests.unit_tests.utils import BaseTest


def on_user_validation(user):
    user.data = "custom"


class Test_UserCreation(BaseTest):
    rest_api_kwargs = {"on_user_validation": on_user_validation}

    def test_main(self):
        name, email, password = "my_user", "a@b.c", "week password"

        with self.api.mail.record_messages() as outbox:
            user = self.create_user(name, email, password).json["user"]
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        self.validate_email(user=user, token=token)
        user = self.get_user(user).json["user"]
        assert user["data"] == "custom"
