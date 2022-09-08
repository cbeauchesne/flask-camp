from tests.utils import BaseTest


class Test_Protection(BaseTest):
    def test_not_allowed(self, client):
        user = self.add_user()

        r = client.put(f"/block_user/{user.id}")
        assert r.status_code == 403

        r = client.delete(f"/block_user/{user.id}")
        assert r.status_code == 403

        self.login_user(client)

        r = client.put(f"/block_user/{user.id}")
        assert r.status_code == 403

        r = client.delete(f"/block_user/{user.id}")
        assert r.status_code == 403

    def test_not_found(self, client):
        moderator = self.add_user(roles="moderator")
        self.login_user(client)

        r = client.put(f"/block_user/42")
        assert r.status_code == 404

        r = client.delete(f"/block_user/42")
        assert r.status_code == 404

    def test_typical_scenario(self, client):
        moderator = self.add_user(roles="moderator")
        user = self.add_user(name="regular_user")

        # log moderator, create a doc
        self.login_user(client)

        doc = client.put("/documents", json={"document": {"namespace": "x", "value": "42"}}).json["document"]

        # now get the user, check its blocked status, and block him
        r = client.get(f"/user/{user.id}")
        assert r.json["user"]["blocked"] == False

        r = client.put(f"/block_user/{user.id}")
        assert r.status_code == 200

        r = client.put(f"/block_user/{user.id}")  # block him twice, it should not produce an error
        assert r.status_code == 200

        r = client.get(f"/user/{user.id}")  # it's status is now blocked
        assert r.json["user"]["blocked"] == True

        self.logout_user(client)

        # user login and try to add/modify a doc
        r = self.login_user(client, user.name)
        assert r.status_code == 200

        r = client.put("/documents", json={"document": {"namespace": "x", "value": "42"}})
        assert r.status_code == 403

        r = client.post(f"/document/{doc['id']}", json={"document": {"namespace": "x", "value": "42"}})
        assert r.status_code == 403

        # logout the user, login the admin, unblock the user
        self.logout_user(client)
        self.login_user(client)

        r = client.delete(f"/block_user/{user.id}")
        assert r.status_code == 200

        r = client.delete(f"/block_user/{user.id}")  # unblock him twice, it should not produce an error
        assert r.status_code == 200

        r = client.get(f"/user/{user.id}")
        assert r.json["user"]["blocked"] == False

        # logout the admin, login the user, try to add/modify
        self.logout_user(client)
        self.login_user(client)

        r = client.put("/documents", json={"document": {"namespace": "x", "value": "42"}})
        assert r.status_code == 200

        r = client.post(f"/document/{doc['id']}", json={"document": {"namespace": "x", "value": "42"}})
        assert r.status_code == 200
