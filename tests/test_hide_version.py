from tests.utils import BaseTest


class Test_HideVersion(BaseTest):
    def hide_version(self, doc, expected_status=200):
        r = self.put(f"/hide_version/{doc['version_id']}")
        assert r.status_code == expected_status

        return r

    def unhide_version(self, doc, expected_status=200):
        r = self.delete(f"/hide_version/{doc['version_id']}")
        assert r.status_code == expected_status

        return r

    def get_document(self, document_id, data_should_be_present, version_should_be=None):
        r = self.get(f"/document/{document_id}")
        assert r.status_code == 200
        if data_should_be_present:
            assert "data" in r.json["document"]
        else:
            assert "data" not in r.json["document"]

        if version_should_be:
            assert r.json["document"]["version_id"] == version_should_be["version_id"]

    def get_document_version(self, version, data_should_be_present):
        r = self.get(f"/document_version/{version['version_id']}")
        assert r.status_code == 200
        if data_should_be_present:
            assert "data" in r.json["document"]
        else:
            assert "data" not in r.json["document"]

    def test_typical(self):
        self.add_user("modo", roles="moderator")
        self.add_user("user")

        self.login_user("modo")

        doc_v1 = self.put_document(data="v1").json["document"]
        doc_v2 = self.post_document(doc_v1["id"], data="v2").json["document"]

        self.hide_version(doc_v1)

        changes = self.get("/changes", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["version_id"] == doc_v1["version_id"]
        assert changes[1]["hidden"] is True
        assert changes[1]["data"] == "v1"
        assert changes[0]["version_id"] == doc_v2["version_id"]
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.logout_user()

        changes = self.get("/changes", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is True
        assert "data" not in changes[1]

        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.login_user("user")
        changes = self.get("/changes", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is True
        assert "data" not in changes[1]
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"
        self.logout_user()

        self.login_user("modo")
        self.unhide_version(doc_v1)

        changes = self.get("/changes", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is False
        assert changes[1]["data"] == "v1"
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

        self.logout_user()

        changes = self.get("/changes", query_string={"document_id": doc_v1["id"]}).json["changes"]
        assert changes[1]["hidden"] is False
        assert changes[1]["data"] == "v1"
        assert changes[0]["hidden"] is False
        assert changes[0]["data"] == "v2"

    def test_forbidden(self):

        # anonymous
        r = self.put("/hide_version/1")
        assert r.status_code == 403
        r = self.delete("/hide_version/1")
        assert r.status_code == 403

        # authenticated
        self.add_user()
        self.login_user()
        r = self.put("/hide_version/1")
        assert r.status_code == 403
        r = self.delete("/hide_version/1")
        assert r.status_code == 403
        self.logout_user()

        self.add_user("admin", roles="admin")
        self.login_user("admin")
        r = self.put("/hide_version/1")
        assert r.status_code == 403
        r = self.delete("/hide_version/1")
        assert r.status_code == 403

    def test_notfound(self):
        self.add_user(roles="moderator")
        self.login_user()
        r = self.put("/hide_version/1")
        assert r.status_code == 404
        r = self.delete("/hide_version/1")
        assert r.status_code == 404

    def test_hide_last(self):

        self.add_user(roles="moderator")
        self.login_user()

        doc_v1 = self.put_document(data="v1").json["document"]
        doc_v2 = self.post_document(doc_v1["id"], data="v2").json["document"]
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
