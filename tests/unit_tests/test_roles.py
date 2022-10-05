from collections import namedtuple

import pytest

from tests.unit_tests.utils import BaseTest
from flask_camp import Application
from flask_camp.application import ConfigurationError


def get_config(roles):
    return namedtuple("Config", ["SECRET_KEY", "POSSIBLE_USER_ROLES", "MAIL_DEFAULT_SENDER"])(
        "qwerty",
        roles,
        "admin@example.com",
    )


class Test_Roles(BaseTest):
    def test_attribution(self, admin, user):
        self.login_user(user)
        self.get("/bot", expected_status=403)

        self.login_user(admin)
        self.add_user_role(user, "bot", "it's a good bot")

        self.login_user(user)
        self.get("/bot", expected_status=200)

    def test_errors(self, admin, user):
        self.login_user(admin)
        r = self.add_user_role(user, "imaginary_role", "comment", expected_status=400).json

        message = "'imaginary_role' doesn't exists. Possible roles are ['admin', 'bot', 'contributor', 'moderator']."
        assert r["description"] == message

    def test_configuration(self):

        app = Application(config_object=get_config("bot"))
        assert "bot" in app.possible_user_roles

        app = Application(config_object=get_config("BOT"))
        assert "bot" in app.possible_user_roles

        app = Application(config_object=get_config("bot, contributor,"))
        assert "bot" in app.possible_user_roles
        assert "contributor" in app.possible_user_roles
        assert "" not in app.possible_user_roles

        app = Application(config_object=get_config(""))
        assert "" not in app.possible_user_roles

    def test_configuration_errors(self):

        with pytest.raises(ConfigurationError):
            Application(config_object=get_config("anonymous"))

        with pytest.raises(ConfigurationError):
            Application(config_object=get_config("authenticated"))
