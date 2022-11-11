import re

from tests.unit_tests.utils import BaseTest


def before_validate_user(user):
    user.data = "custom"


class Test_UserCreation(BaseTest):
    rest_api_kwargs = {"before_validate_user": before_validate_user}

    def test_main(self):
        name, email, password = "my_user", "a@b.c", "week password"

        with self.api.mail.record_messages() as outbox:
            user = self.create_user(name, email, password).json["user"]
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        self.validate_email(user=user, token=token)
        user = self.login_user(user, password=password).json["user"]
        assert user["data"] == "custom"
