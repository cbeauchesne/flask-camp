import pytest

from flask_camp.models import User
from flask_camp._schemas import schema
from tests.unit_tests.utils import BaseTest


def test_missing_schema():
    with pytest.raises(FileNotFoundError):
        schema("Idonotexists")


class Test_Vuln(BaseTest):
    def test_vuln(self, user, user_2):
        @self.app.route("/__testing/vuln/<int:user_id>", methods=["GET"])
        def testing_vuln(user_id):
            """Calling this method without being authentified as user_id mys raise a Forbidden response"""
            return User.get(id=user_id).as_dict(include_personal_data=True)

        self.get(f"/__testing/vuln/{user.id}", expected_status=403)

        self.login_user(user)
        self.get(f"/__testing/vuln/{user_2.id}", expected_status=403)

        self.get(f"/__testing/vuln/{user.id}", expected_status=200)


class Test_Errors(BaseTest):
    def test_no_body(self, user):
        self.login_user(user)

        r = self.put("/documents", data="null", expected_status=400)
        assert r.json is not None

        r = self.put("/documents", data="null", headers={"Content-Type": "application/json"}, expected_status=400)
        assert r.json is not None
        assert r.json["description"] == "None is not of type 'object' on instance ", r.json

    def test_main(self):
        r = self.get("/do_not_exists", expected_status=404)
        assert r.json is not None
        assert r.json["status"] == "error"

        r = self.delete("/healthcheck", expected_status=405)
        assert r.json is not None
        assert r.json["status"] == "error"
