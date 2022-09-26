from tests.unit_tests.utils import BaseTest


class Test_CurrentUser(BaseTest):
    def get_current_user(self, expected_status=200):
        return self.get("/current_user", expected_status=expected_status)

    def test_anonymous(self):
        self.get_current_user(expected_status=403)

    def test_basic(self, user):
        self.login_user(user)
        r = self.get_current_user(expected_status=200)

        assert "user" in r.json
