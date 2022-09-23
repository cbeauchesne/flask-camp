from tests.unit_tests.utils import BaseTest


class Test_Admin(BaseTest):
    def test_right_attribution(self, admin, user):
        self.login_user(user)

        r = self.modify_user(user, roles=["moderator"], expected_status=200)

        r = self.get(f"/user/{user.id}", expected_status=200)
        assert r.json["user"]["roles"] == []

        self.logout_user()

        self.login_user(admin)
        r = self.modify_user(user, roles=["moderator"], expected_status=200)
        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["roles"] == ["moderator"]

    def test_init_database(self):
        r = self.get("/init_database", expected_status=200)

        r = self.get("/user/1", expected_status=200)
        assert r.json["user"]["name"] == "admin"
