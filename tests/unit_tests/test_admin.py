from tests.unit_tests.utils import BaseTest


class Test_Admin(BaseTest):
    def test_right_attribution(self, admin, user):
        self.login_user(user)
        self.modify_user(user, roles=["moderator"], comment="comment", expected_status=403)

        r = self.get_user(user, expected_status=200)
        assert r.json["user"]["roles"] == []
        self.logout_user()

        self.login_user(admin)
        self.modify_user(user, roles=["moderator"], comment="comment", expected_status=200)
        r = self.get_user(user, expected_status=200)
        assert r.json["user"]["roles"] == ["moderator"]
