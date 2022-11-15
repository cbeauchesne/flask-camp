from tests.unit_tests.utils import BaseTest


class Test_HideVersion(BaseTest):
    def test_typical(self, user, moderator):

        self.login_user(moderator)

        doc_v1 = self.create_document(data="v1").json["document"]
        doc_v2 = self.modify_document(doc_v1, data="v2").json["document"]

        self.hide_version(doc_v1)

        changes = self.get_versions(document=doc_v1).json["versions"]
        assert changes[1]["version_id"] == doc_v1["version_id"]
        assert changes[1]["hidden"] is True
        assert changes[1]["data"] == "v1"
        assert changes[0]["version_id"] == doc_v2["version_id"]
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.logout_user()

        changes = self.get_versions(document=doc_v1).json["versions"]
        assert changes[1]["hidden"] is True
        assert "data" not in changes[1]

        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.login_user(user)
        changes = self.get_versions(document=doc_v1).json["versions"]
        assert changes[1]["hidden"] is True
        assert "data" not in changes[1]
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"
        self.logout_user()

        self.login_user(moderator)
        self.unhide_version(doc_v1)

        changes = self.get_versions(document=doc_v1).json["versions"]
        assert changes[1]["hidden"] is False
        assert changes[1]["data"] == "v1"
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.logout_user()

        changes = self.get_versions(document=doc_v1).json["versions"]
        assert changes[1]["hidden"] is False
        assert changes[1]["data"] == "v1"
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

    def test_forbidden(self, user, admin):

        # anonymous
        self.hide_version(1, expected_status=403)
        self.unhide_version(1, expected_status=403)

        # authenticated
        self.login_user(user)
        self.hide_version(1, expected_status=403)
        self.unhide_version(1, expected_status=403)
        self.logout_user()

        self.login_user(admin)
        self.hide_version(1, expected_status=403)
        self.unhide_version(1, expected_status=403)

    def test_notfound(self, moderator):
        self.login_user(moderator)
        self.hide_version(1, expected_status=404)
        self.unhide_version(1, expected_status=404)

    def test_hide_last(self, moderator):
        self.login_user(moderator)

        doc_v1 = self.create_document(data="v1").json["document"]
        doc_v2 = self.modify_document(doc_v1, data="v2").json["document"]

        self.hide_version(doc_v2, expected_status=400)
