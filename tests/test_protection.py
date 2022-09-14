from tests.utils import BaseTest


class Test_Protection(BaseTest):
    def test_errors(self):
        self.db_add_user(roles="moderator")
        self.login_user()

        self.protect_document(42, 404)
        self.unprotect_document(42, 404)

    def test_typical_scenario(self):
        moderator = self.db_add_user(roles="moderator")
        user = self.db_add_user(name="regular_user")

        self.login_user(user.name)
        r = self.create_document()
        document_id = r.json["document"]["id"]

        # try to protect a doc without being an moderator
        r = self.protect_document(document_id, 403)
        self.logout_user()

        # protect doc
        self.login_user(moderator.name)
        r = self.protect_document(document_id)

        r = self.get(f"/document/{document_id}")
        assert r.json["document"]["protected"] is True
        self.logout_user()

        self.login_user(user.name)
        self.protect_document(document_id, expected_status=403)  # unprotect doc without being an moderator
        self.modify_document(document_id, expected_status=403)  # edit protected doc without being an moderator
        self.logout_user()

        self.login_user(moderator.name)
        self.modify_document(document_id, data={"value": "43"}, expected_status=200)  # edit protected doc
        self.unprotect_document(document_id, expected_status=200)  # unprotect doc

        r = self.get(f"/document/{document_id}")
        assert r.json["document"]["protected"] is False
        self.logout_user()

        # edit deprotected doc
        self.login_user(user.name)
        r = self.modify_document(document_id, data={"value": "43"}, expected_status=200)
        assert r.json["document"]["protected"] is False

        # try to hack
        r = self.post(f"/document/{document_id}", json={"document": {"namespace": "x", "protected": True, "data": {}}})
        assert r.status_code == 200, r.json
        assert r.json["document"]["protected"] is False
