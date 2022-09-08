from tests.utils import BaseTest


class Test_Protection(BaseTest):
    def test_errors(self, client):
        moderator = self.add_user(roles="moderator")
        self.login_user(client)

        r = client.put(f"/protect/42")
        assert r.status_code == 404

        r = client.delete(f"/protect/42")
        assert r.status_code == 404

    def test_typical_scenario(self, client):
        moderator = self.add_user(roles="moderator")
        user = self.add_user(name="regular_user")

        self.login_user(client, user.name)
        r = client.put("/documents", json={"document": {"namespace": "x", "value": "42"}})
        document_id = r.json["document"]["id"]

        # try to protect a doc without being an moderator
        r = client.put(f"/protect/{document_id}")
        assert r.status_code == 401
        self.logout_user(client)

        # protect doc
        self.login_user(client, moderator.name)
        r = client.put(f"/protect/{document_id}")
        assert r.status_code == 200
        r = client.get(f"/document/{document_id}")
        assert r.json["document"]["protected"] == True
        self.logout_user(client)

        # try to unprotect doc without being an moderator
        self.login_user(client, user.name)
        r = client.delete(f"/protect/{document_id}")
        assert r.status_code == 401

        # try to edit doc  without being an moderator
        r = client.post(f"/document/{document_id}", json={"document": {"namespace": "x", "value": "42"}})
        assert r.status_code == 401
        self.logout_user(client)

        # edit protected doc
        self.login_user(client, moderator.name)
        r = client.post(f"/document/{document_id}", json={"document": {"namespace": "x", "value": "43"}})
        assert r.status_code == 200

        # unprotect doc
        r = client.delete(f"/protect/{document_id}")
        assert r.status_code == 200
        r = client.get(f"/document/{document_id}")
        assert r.json["document"]["protected"] == False
        self.logout_user(client)

        # edit deprotected doc
        self.login_user(client, user.name)
        r = client.post(f"/document/{document_id}", json={"document": {"namespace": "x", "value": "43"}})
        assert r.status_code == 200
        assert r.json["document"]["protected"] == False

        r = client.post(
            f"/document/{document_id}", json={"document": {"namespace": "x", "value": "44", "protected": True}}
        )
        assert r.status_code == 200
        assert r.json["document"]["protected"] == False
