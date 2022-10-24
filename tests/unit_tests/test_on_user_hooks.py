import re
from unittest.mock import MagicMock

from tests.unit_tests.utils import BaseTest

hooks = MagicMock()


class Test_OnUserUpdate(BaseTest):
    rest_api_kwargs = {
        "on_user_creation": hooks.on_user_creation,
        "on_user_validation": hooks.on_user_validation,
        "on_user_update": hooks.on_user_update,
        "on_user_block": hooks.on_user_block,
    }

    def test_main(self):

        with self.api.mail.record_messages() as outbox:
            user = self.create_user().json["user"]
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        assert hooks.on_user_creation.called
        assert not hooks.on_user_validation.called
        assert not hooks.on_user_update.called

        hooks.reset_mock()
        self.validate_email(user, token)
        assert not hooks.on_user_creation.called
        assert hooks.on_user_validation.called
        assert not hooks.on_user_update.called

        self.login_user(user)

        hooks.reset_mock()
        self.modify_user(user, password="password", new_password="password")
        assert not hooks.on_user_creation.called
        assert not hooks.on_user_validation.called
        assert hooks.on_user_update.called

        hooks.reset_mock()
        self.modify_user(user, ui_preferences="12")
        assert not hooks.on_user_creation.called
        assert not hooks.on_user_validation.called
        assert hooks.on_user_update.called

        hooks.reset_mock()
        with self.api.mail.record_messages() as outbox:
            self.modify_user(user, password="password", email="new@mail.fr")
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        assert not hooks.on_user_creation.called
        assert not hooks.on_user_validation.called
        assert hooks.on_user_update.called

        hooks.reset_mock()
        self.validate_email(user, token)
        assert not hooks.on_user_creation.called
        assert not hooks.on_user_validation.called
        assert hooks.on_user_update.called

    def test_user_block(self, moderator, user):
        self.login_user(moderator)

        self.block_user(user)
        assert hooks.on_user_block.called

        hooks.reset_mock()
        self.unblock_user(user)
        assert hooks.on_user_block.called
