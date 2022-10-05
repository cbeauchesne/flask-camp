# pylint: disable=too-few-public-methods

import pytest

from wiki_api import Application
from wiki_api.application import ConfigurationError


class Config:
    SECRET_KEY = "qwerty"
    MAIL_DEFAULT_SENDER = "admin@example.com"


class Test_AddModule:
    def test_main(self):
        app = Application(Config)

        class CustomModule:
            rule = "/endpoint"

            @app.allow("anonymous")
            def get(self):
                pass

        app.add_modules(CustomModule)

        rules = {url_rule.rule for url_rule in app.url_map.iter_rules()}

        assert CustomModule.rule in rules, rules


class Test_Errors:
    def test_missing_allowed(self):
        app = Application(Config)

        class CustomModule:
            rule = "/endpoint"

            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            app.add_modules(CustomModule)

    def test_missing_rule(self):
        app = Application(Config)

        class CustomModule:
            @app.allow("anonymous")
            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            app.add_modules(CustomModule)

    def test_roles_doesnt_exists(self):
        app = Application(Config)

        class CustomModule:
            rule = "/endpoint"

            @app.allow("not-a-role")
            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            app.add_modules(CustomModule)

    def test_twice(self):
        app = Application(Config)

        class CustomModule:
            rule = "/endpoint"

            @app.allow("anonymous")
            def get(self):
                pass

        with pytest.raises(AssertionError):
            app.add_modules(CustomModule, CustomModule)
