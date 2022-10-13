import pytest

from flask_camp import RestApi
from flask_camp.exceptions import ConfigurationError
from tests.unit_tests.utils import BaseTest


class Test_UrlPrefix(BaseTest):
    rest_api_kwargs = {"url_prefix": "/v7"}

    def test_main(self):
        class Route:
            rule = "/hello"

            @self.api.allow("anonymous")
            def get(self):
                return "hello"

        self.api.add_modules(self.app, Route(), url_prefix="")

        self.get("/v7/", expected_status=200)
        self.get("/hello", expected_status=200)


def test_not_leading_slash():
    with pytest.raises(ConfigurationError):
        RestApi(url_prefix="v7")

    with pytest.raises(ConfigurationError):
        api = RestApi()
        api.add_modules(None, url_prefix="v7")


def test_tailing_slash():
    with pytest.raises(ConfigurationError):
        RestApi(url_prefix="/v7/")

    with pytest.raises(ConfigurationError):
        api = RestApi()
        api.add_modules(None, None, url_prefix="/v7/")
