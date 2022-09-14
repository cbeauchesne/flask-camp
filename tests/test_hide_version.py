from tests.utils import BaseTest


class Test_HideVersion(BaseTest):
    def test_typical(self):
        self.db_add_user("modo", roles="moderator")
        self.db_add_user("user")

        self.login_user("modo")

        doc_v1 = self.create_document(data="v1").json["document"]
        doc_v2 = self.modify_document(doc_v1["id"], data="v2").json["document"]

        self.hide_version(doc_v1)

        changes = self.get("/document_versions", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["version_id"] == doc_v1["version_id"]
        assert changes[1]["hidden"] is True
        assert changes[1]["data"] == "v1"
        assert changes[0]["version_id"] == doc_v2["version_id"]
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.logout_user()

        changes = self.get("/document_versions", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is True
        assert "data" not in changes[1]

        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.login_user("user")
        changes = self.get("/document_versions", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is True
        assert "data" not in changes[1]
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"
        self.logout_user()

        self.login_user("modo")
        self.unhide_version(doc_v1)

        changes = self.get("/document_versions", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is False
        assert changes[1]["data"] == "v1"
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.logout_user()

        changes = self.get("/document_versions", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is False
        assert changes[1]["data"] == "v1"
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

    def test_forbidden(self):

        # anonymous
        self.hide_version(1, expected_status=403)
        self.unhide_version(1, expected_status=403)

        # authenticated
        self.db_add_user()
        self.login_user()
        self.hide_version(1, expected_status=403)
        self.unhide_version(1, expected_status=403)
        self.logout_user()

        self.db_add_user("admin", roles="admin")
        self.login_user("admin")
        self.hide_version(1, expected_status=403)
        self.unhide_version(1, expected_status=403)

    def test_notfound(self):
        self.db_add_user(roles="moderator")
        self.login_user()
        self.hide_version(1, expected_status=404)
        self.unhide_version(1, expected_status=404)

    def test_hide_last(self):

        self.db_add_user(roles="moderator")
        self.login_user()

        doc_v1 = self.create_document(data="v1").json["document"]
        doc_v2 = self.modify_document(doc_v1["id"], data="v2").json["document"]
        document_id = doc_v1["id"]

        # state 1: only V2 is hidden (it's the last one)
        self.login_user()
        self.hide_version(doc_v2)

        # for modo/admins
        self.get_document(document_id, data_should_be_present=True, version_should_be=doc_v1)
        self.get_document_version(doc_v1, data_should_be_present=True)
        self.get_document_version(doc_v2, data_should_be_present=True)

        # for other users
        self.logout_user()
        self.get_document(document_id, data_should_be_present=True, version_should_be=doc_v1)
        self.get_document_version(doc_v1, data_should_be_present=True)
        self.get_document_version(doc_v2, data_should_be_present=False)

        ## state 2 : V1 and V2 are hidden
        self.login_user()
        self.hide_version(doc_v1)

        # for modo/admins
        self.get_document(document_id, data_should_be_present=False)
        self.get_document_version(doc_v1, data_should_be_present=True)
        self.get_document_version(doc_v2, data_should_be_present=True)

        # for other users
        self.logout_user()
        self.get_document(document_id, data_should_be_present=False)
        self.get_document_version(doc_v1, data_should_be_present=False)
        self.get_document_version(doc_v2, data_should_be_present=False)