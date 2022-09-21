from tests.unit_tests.utils import BaseTest


class Test_Admin(BaseTest):
    def test_right_attribution(self, admin, user):
        self.login_user(user)

        r = self.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json

        r = self.get(f"/user/{user.id}")
        assert r.status_code == 200, r.json
        assert r.json["user"]["roles"] == []

        self.logout_user()

        self.login_user(admin)
        r = self.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json
        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["roles"] == ["moderator"]

    def test_init_database(self):
        r = self.get("/init_database")
        assert r.status_code == 200

        r = self.get("/user/1")
        assert r.status_code == 200
        assert r.json["user"]["name"] == "admin"
