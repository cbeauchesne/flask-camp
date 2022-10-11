import pytest

from tests.unit_tests.utils import BaseTest
from flask_camp import RestApi, allow
from flask_camp.exceptions import ConfigurationError


class BotModule:
    rule = "/bot"

    @staticmethod
    @allow("bot")
    def get():
        """Here is a custom post, only for bots"""
        return {"hello": "world"}


class Test_Roles(BaseTest):
    rest_api_kwargs = {"user_roles": "bot,contributor"}

    def test_attribution(self, admin, user):
        self.api.add_modules(self.app, BotModule())

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


class Test_Configuration(BaseTest):
    def test_configuration(self):

        api = RestApi(user_roles="bot")
        assert "bot" in api.user_roles

        api = RestApi(user_roles="BOT")
        assert "bot" in api.user_roles

        api = RestApi(user_roles="bot, contributor,")
        assert "bot" in api.user_roles
        assert "contributor" in api.user_roles
        assert "" not in api.user_roles

        api = RestApi(user_roles="")
        assert "" not in api.user_roles

    def test_configuration_errors(self):

        with pytest.raises(ConfigurationError):
            RestApi(user_roles="anonymous")

        with pytest.raises(ConfigurationError):
            RestApi(user_roles="authenticated")
