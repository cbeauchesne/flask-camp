from tests.unit_tests.utils import BaseTest


class Test_Admin(BaseTest):
    def test_right_attribution(self, admin, user):
        self.login_user(user)
        self.add_user_role(user, "moderator", "comment", expected_status=403)

        r = self.get_user(user, expected_status=200)
        assert r.json["user"]["roles"] == []
        self.logout_user()

        self.login_user(admin)
        self.add_user_role(user, "moderator", "comment", expected_status=200)
        r = self.get_user(user, expected_status=200)
        assert r.json["user"]["roles"] == ["moderator"]
