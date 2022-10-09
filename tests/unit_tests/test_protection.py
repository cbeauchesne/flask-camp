from tests.unit_tests.utils import BaseTest


class Test_Protection(BaseTest):
    def test_errors(self, moderator):
        self.login_user(moderator)

        document = self.create_document().json["document"]

        self.protect_document(42, expected_status=404)
        self.unprotect_document(42, expected_status=404)

        self.protect_document(document)
        self.protect_document(document, expected_status=400)

        self.unprotect_document(document)
        self.unprotect_document(document, expected_status=400)

    def test_typical_scenario(self, user, moderator):
        self.login_user(user)
        v0 = self.create_document().json["document"]
        document = v0  # more clear

        # try to protect a doc without being an moderator
        r = self.protect_document(document, expected_status=403)
        self.logout_user()

        # protect doc
        self.login_user(moderator)
        r = self.protect_document(document)

        r = self.get_document(document)
        assert r.json["document"]["protected"] is True
        self.logout_user()

        self.login_user(user)
        self.protect_document(document, expected_status=403)  # unprotect doc without being an moderator
        self.modify_document(v0, expected_status=403)  # edit protected doc without being an moderator
        self.logout_user()

        self.login_user(moderator)
        v1 = self.modify_document(v0, data={"value": "43"}, expected_status=200).json["document"]  # edit protected doc
        self.unprotect_document(document, expected_status=200)  # unprotect doc

        r = self.get_document(document)
        assert r.json["document"]["protected"] is False
        self.logout_user()

        # edit deprotected doc
        self.login_user(user)
        v2 = self.modify_document(v1, data={"value": "44"}, expected_status=200).json["document"]
        assert r.json["document"]["protected"] is False

        # try to hack
        v2["protected"] = True
        v3 = self.modify_document(v2, data={"value": "45"}, expected_status=200).json["document"]
        assert v3["protected"] is False
