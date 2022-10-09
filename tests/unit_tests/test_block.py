from tests.unit_tests.utils import BaseTest


# TODO : test block when user is currently logged in


class Test_UserBlock(BaseTest):
    def test_not_allowed(self, user):
        self.block_user(user, expected_status=403)
        self.unblock_user(user, expected_status=403)

        self.login_user(user)

        self.block_user(user, expected_status=403)
        self.unblock_user(user, expected_status=403)

    def test_not_found(self, moderator):
        self.login_user(moderator)

        self.block_user(42, expected_status=404)
        self.unblock_user(42, expected_status=404)

    def test_typical_scenario(self, moderator, user):
        # log moderator, create a doc
        self.login_user(moderator)

        doc = self.create_document().json["document"]

        # now get the user, check its blocked status, and block him
        r = self.get_user(user)
        assert r.json["user"]["blocked"] is False

        self.block_user(user)
        self.block_user(user, expected_status=400)  # block him twice, it should produce an bad request error

        r = self.get_user(user)  # it's status is now blocked
        assert r.json["user"]["blocked"] is True

        self.logout_user()

        # user login and try to get/add/modify a doc
        self.login_user(user, expected_status=200)
        self.get_document(doc, expected_status=200)
        self.get_documents(expected_status=200)

        self.create_document(expected_status=403)
        self.modify_document(doc, expected_status=403)

        # Though, he can modify itself
        self.modify_user(user, new_password="updated", password="password", expected_status=200)

        # even get users, or one user
        self.get_user(moderator, expected_status=200)

        # logout the user, login the moderator, unblock the user
        self.logout_user()
        self.login_user(moderator)

        self.unblock_user(user)
        self.unblock_user(user, expected_status=400)  # unblock him twice, it should produce a bad request error

        r = self.get_user(user)
        assert not r.json["user"]["blocked"]

        # logout the admin, login the user, try to add/modify
        self.logout_user()
        self.login_user(user, password="updated")

        self.create_document(expected_status=200)
        self.modify_document(doc, data={"value": "42"}, expected_status=200)
