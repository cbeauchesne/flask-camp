import pytest

from cms.schemas import schema
from tests.utils import BaseTest


def test_missing_schema():
    with pytest.raises(FileNotFoundError):
        schema("Idonotexists")


class Test_Errors(BaseTest):
    def test_no_body(self, user):
        self.login_user(user)

        r = self.put("/documents", data="null")
        assert r.status_code == 400
        assert r.json is not None

        r = self.put("/documents", data="null", headers={"Content-Type": "application/json"})
        assert r.status_code == 400
        assert r.json is not None
        assert r.json["description"] == "None is not of type 'object' on instance ", r.json

    def test_vuln(self, user, user_2):

        r = self.client.get(f"/__testing/vuln/{user.id}")
        assert r.status_code == 403

        self.login_user(user)
        r = self.client.get(f"/__testing/vuln/{user_2.id}")
        assert r.status_code == 403

        r = self.client.get(f"/__testing/vuln/{user.id}")
        assert r.status_code == 200

    def test_main(self):
        r = self.get("/do_not_exists")
        assert r.status_code == 404
        assert r.json is not None
        assert r.json["status"] == "error"

        r = self.delete("/healthcheck")
        assert r.status_code == 405
        assert r.json is not None
        assert r.json["status"] == "error"

    # def test_500(self):
    #     r = self.get("/__testing/500")
    #     assert r.status_code == 500, r
    #     assert r.json is not None, r
    #     assert "status" in r.json, r.json
    #     assert "description" in r.json, r.json

    #     description = (
    #         "The server encountered an internal error and was unable to complete your request. "
    #         "Either the server is overloaded or there is an error in the application."
    #     )
    #     assert r.json["status"] == "error", r.json
    #     assert r.json["name"] == "Internal Server Error", r.json
    #     assert r.json["description"] == description, r.json
