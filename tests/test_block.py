from tests.utils import BaseTest


# TODO : test block when user is currently logged in


class Test_Protection(BaseTest):
    def test_not_allowed(self):
        user = self.db_add_user()

        self.block_user(user, 403)
        self.unblock_user(user, 403)

        self.login_user()

        self.block_user(user, 403)
        self.unblock_user(user, 403)

    def test_not_found(self):
        self.db_add_user(roles="moderator")
        self.login_user()

        r = self.put("/block_user/42", json={"comment": "some comment"})
        assert r.status_code == 404, r.json

        r = self.delete("/block_user/42", json={"comment": "some comment"})
        assert r.status_code == 404, r.json

    def test_typical_scenario(self):
        moderator = self.db_add_user(roles="moderator")
        user = self.db_add_user(name="regular_user")

        # log moderator, create a doc
        self.login_user()

        doc = self.create_document().json["document"]

        # now get the user, check its blocked status, and block him
        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["blocked"] is False

        self.block_user(user)
        self.block_user(user)  # block him twice, it should not produce an error

        r = self.get(f"/user/{user.id}")  # it's status is now blocked
        assert r.json["user"]["blocked"] is True

        self.logout_user()

        # user login and try to get/add/modify a doc
        r = self.login_user(user.name)
        assert r.status_code == 200

        r = self.get(f"/document/{doc['id']}")
        assert r.status_code == 200

        r = self.get("/documents")
        assert r.status_code == 200

        self.create_document(expected_status=403)
        self.modify_document(doc["id"], expected_status=403)

        # Though, he can modify itself
        r = self.post(f"/user/{user.id}", json={"password": "updated"})
        assert r.status_code == 200

        # even get users, or one user
        r = self.get(f"/user/{moderator.id}")
        assert r.status_code == 200

        # logout the user, login the admin, unblock the user
        self.logout_user()
        self.login_user()

        self.unblock_user(user)
        self.unblock_user(user)  # unblock him twice, it should not produce an error

        r = self.get(f"/user/{user.id}")
        assert not r.json["user"]["blocked"]

        # logout the admin, login the user, try to add/modify
        self.logout_user()
        self.login_user()

        self.create_document(expected_status=200)
        self.modify_document(doc["id"], data={"value": "42"}, expected_status=200)
