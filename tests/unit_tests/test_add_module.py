import pytest

from flask_camp.exceptions import ConfigurationError

from tests.unit_tests.utils import BaseTest


class Test_ClassInstance(BaseTest):
    def test_main(self):
        class CustomModule:
            rule = "/endpoint"

            @self.api.allow("anonymous")
            def get(self):
                return "ok"

        self.api.add_modules(self.app, CustomModule())

        rules = {url_rule.rule for url_rule in self.app.url_map.iter_rules()}

        assert CustomModule.rule in rules, rules

        self.get("/endpoint", expected_status=200)


class Test_Class(BaseTest):
    def test_main(self):
        class CustomModule:
            rule = "/endpoint"

            @staticmethod
            @self.api.allow("anonymous")
            def get():
                return "ok"

        self.api.add_modules(self.app, CustomModule)

        rules = {url_rule.rule for url_rule in self.app.url_map.iter_rules()}

        assert CustomModule.rule in rules, rules

        self.get("/endpoint", expected_status=200)


class Test_Errors(BaseTest):
    def test_missing_allowed(self):
        class CustomModule:
            rule = "/endpoint"

            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            self.api.add_modules(self.app, CustomModule)

    def test_missing_rule(self):
        class CustomModule:
            @self.api.allow("anonymous")
            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            self.api.add_modules(self.app, CustomModule)

    def test_roles_doesnt_exists(self):
        class CustomModule:
            rule = "/endpoint"

            @self.api.allow("not-a-role")
            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            self.api.add_modules(self.app, CustomModule)

    def test_twice(self):
        class CustomModule:
            rule = "/endpoint"

            @self.api.allow("anonymous")
            def get(self):
                pass

        with pytest.raises(AssertionError):
            self.api.add_modules(self.app, CustomModule, CustomModule)
