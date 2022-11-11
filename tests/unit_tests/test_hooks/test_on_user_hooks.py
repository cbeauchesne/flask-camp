import re
from unittest.mock import MagicMock

from tests.unit_tests.utils import BaseTest

hooks = MagicMock()


class Test_OnUserUpdate(BaseTest):
    rest_api_kwargs = {
        "before_create_user": hooks.before_create_user,
        "before_validate_user": hooks.before_validate_user,
        "before_update_user": hooks.before_update_user,
        "before_block_user": hooks.before_block_user,
    }

    def test_main(self):

        with self.api.mail.record_messages() as outbox:
            user = self.create_user().json["user"]
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        assert hooks.before_create_user.called
        assert not hooks.before_validate_user.called
        assert not hooks.before_update_user.called

        hooks.reset_mock()
        self.validate_email(user, token)
        assert not hooks.before_create_user.called
        assert hooks.before_validate_user.called
        assert not hooks.before_update_user.called

        self.login_user(user)

        hooks.reset_mock()
        self.modify_user(user, password="password", new_password="password")
        assert not hooks.before_create_user.called
        assert not hooks.before_validate_user.called
        assert hooks.before_update_user.called

        hooks.reset_mock()
        self.modify_user(user, data="12")
        assert not hooks.before_create_user.called
        assert not hooks.before_validate_user.called
        assert hooks.before_update_user.called

        hooks.reset_mock()
        with self.api.mail.record_messages() as outbox:
            self.modify_user(user, password="password", email="new@mail.fr")
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        assert not hooks.before_create_user.called
        assert not hooks.before_validate_user.called
        assert hooks.before_update_user.called

        hooks.reset_mock()
        self.validate_email(user, token)
        assert not hooks.before_create_user.called
        assert not hooks.before_validate_user.called
        assert hooks.before_update_user.called

    def test_user_block(self, moderator, user):
        self.login_user(moderator)

        self.block_user(user)
        assert hooks.before_block_user.called

        hooks.reset_mock()
        self.unblock_user(user)
        assert hooks.before_block_user.called
