# pylint: disable=too-few-public-methods

import pytest

from flask_camp import RestApi
from flask_camp.exceptions import ConfigurationError

from tests.unit_tests.utils import create_test_app


def create_api():
    app = create_test_app()
    api = RestApi(app)

    return app, api


class Test_AddModule:
    def test_main(self):
        app, api = create_api()

        class CustomModule:
            rule = "/endpoint"

            @api.allow("anonymous")
            def get(self):
                pass

        api.add_modules(app, CustomModule)

        rules = {url_rule.rule for url_rule in app.url_map.iter_rules()}

        assert CustomModule.rule in rules, rules


class Test_Errors:
    def test_missing_allowed(self):
        app, api = create_api()

        class CustomModule:
            rule = "/endpoint"

            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            api.add_modules(app, CustomModule)

    def test_missing_rule(self):
        app, api = create_api()

        class CustomModule:
            @api.allow("anonymous")
            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            api.add_modules(app, CustomModule)

    def test_roles_doesnt_exists(self):
        app, api = create_api()

        class CustomModule:
            rule = "/endpoint"

            @api.allow("not-a-role")
            def get(self):
                pass

        with pytest.raises(ConfigurationError):
            api.add_modules(app, CustomModule)

    def test_twice(self):
        app, api = create_api()

        class CustomModule:
            rule = "/endpoint"

            @api.allow("anonymous")
            def get(self):
                pass

        with pytest.raises(AssertionError):
            api.add_modules(app, CustomModule, CustomModule)
