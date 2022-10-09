import pytest

from tests.unit_tests.utils import BaseTest
from flask_camp import RestApi
from flask_camp.exceptions import ConfigurationError


class Test_Namespaces(BaseTest):
    def test_errors(self, user):
        self.login_user(user)

        r = self.create_document(namespace="not-a-namespace", expected_status=400).json
        message = "'not-a-namespace' is not a valid namespace."
        assert r["description"] == message

    def test_configuration(self):

        api = RestApi(namespaces=["", "profile"])
        assert "" in api.namespaces
        assert "profile" in api.namespaces

        api = RestApi(namespaces="outing,profile")
        assert "outing" in api.namespaces
        assert "profile" in api.namespaces

        api = RestApi(namespaces="PROFILE")
        assert "profile" in api.namespaces

        api = RestApi(namespaces=" no-space")
        assert "no-space" in api.namespaces

        api = RestApi(namespaces="bot, contributor,")
        assert "bot" in api.namespaces
        assert "contributor" in api.namespaces
        assert "" in api.namespaces

        api = RestApi(namespaces="")
        assert "" in api.namespaces

        api = RestApi()
        assert api.namespaces is None

    def test_configuration_errors(self):

        with pytest.raises(ConfigurationError):
            RestApi(namespaces="a" * 17)

        with pytest.raises(ConfigurationError):
            RestApi(namespaces="a a")
