from tests.unit_tests.utils import BaseTest


class Test_RenameUser(BaseTest):
    def test_not_allowed(self, user, user_2):
        self.rename_user(user, "toto", expected_status=403)
        self.rename_user(user_2, "toto", expected_status=403)

        self.login_user(user)

        self.block_user(user, expected_status=403)
        self.unblock_user(user, expected_status=403)

    def test_main(self, user, moderator):
        self.login_user(moderator)

        r = self.get_user(user)
        assert r.json["user"]["name"] == user.name

        self.rename_user(user, "new_name")

        r = self.get_user(user)
        assert r.json["user"]["name"] == "new_name"

    def test_errors(self, user, moderator):
        self.login_user(moderator)

        self.rename_user(42, "toto", expected_status=404)
        self.rename_user(user, "@not_a_good_name", expected_status=400)
