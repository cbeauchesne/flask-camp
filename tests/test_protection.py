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
        v0 = self.create_document().json["document"]
        document_id = v0["id"]

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
        self.modify_document(v0, expected_status=403)  # edit protected doc without being an moderator
        self.logout_user()

        self.login_user(moderator.name)
        v1 = self.modify_document(v0, data={"value": "43"}, expected_status=200).json["document"]  # edit protected doc
        self.unprotect_document(document_id, expected_status=200)  # unprotect doc

        r = self.get(f"/document/{document_id}")
        assert r.json["document"]["protected"] is False
        self.logout_user()

        # edit deprotected doc
        self.login_user(user.name)
        v2 = self.modify_document(v1, data={"value": "44"}, expected_status=200).json["document"]
        assert r.json["document"]["protected"] is False

        # try to hack
        v2["protected"] = True
        v3 = self.modify_document(v2, data={"value": "45"}, expected_status=200).json["document"]
        assert v3["protected"] is False
