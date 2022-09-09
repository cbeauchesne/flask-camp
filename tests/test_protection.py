from tests.utils import BaseTest


class Test_Protection(BaseTest):
    def test_errors(self):
        self.add_user(roles="moderator")
        self.login_user()

        r = self.put("/protect/42")
        assert r.status_code == 404

        r = self.delete("/protect/42")
        assert r.status_code == 404

    def test_typical_scenario(self):
        moderator = self.add_user(roles="moderator")
        user = self.add_user(name="regular_user")

        self.login_user(user.name)
        r = self.put_document()
        document_id = r.json["document"]["id"]

        # try to protect a doc without being an moderator
        r = self.put(f"/protect/{document_id}")
        assert r.status_code == 403
        self.logout_user()

        # protect doc
        self.login_user(moderator.name)
        r = self.put(f"/protect/{document_id}")
        assert r.status_code == 200
        r = self.get(f"/document/{document_id}")
        assert r.json["document"]["protected"] is True
        self.logout_user()

        # try to unprotect doc without being an moderator
        self.login_user(user.name)
        r = self.delete(f"/protect/{document_id}")
        assert r.status_code == 403

        # try to edit doc without being an moderator
        r = self.post_document(document_id)
        assert r.status_code == 403
        self.logout_user()

        # edit protected doc
        self.login_user(moderator.name)
        r = self.post_document(document_id, data={"value": "43"})
        assert r.status_code == 200

        # unprotect doc
        r = self.delete(f"/protect/{document_id}")
        assert r.status_code == 200
        r = self.get(f"/document/{document_id}")
        assert r.json["document"]["protected"] is False
        self.logout_user()

        # edit deprotected doc
        self.login_user(user.name)
        r = self.post_document(document_id, data={"value": "43"})
        assert r.status_code == 200
        assert r.json["document"]["protected"] is False

        # try to hack
        r = self.post(f"/document/{document_id}", json={"document": {"namespace": "x", "protected": True, "data": {}}})
        assert r.status_code == 200, r.json
        assert r.json["document"]["protected"] is False
