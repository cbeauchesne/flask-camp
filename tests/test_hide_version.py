from tests.utils import BaseTest


class Test_HideVersion(BaseTest):
    def test_typical(self):
        self.add_user("modo", roles="moderator")
        self.add_user("user")

        self.login_user("modo")

        doc_v1 = self.put_document(data="v1").json["document"]
        doc_v2 = self.post_document(doc_v1["id"], data="v2").json["document"]

        r = self.put(f"/hide_version/{doc_v1['version_id']}")
        assert r.status_code == 200

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
        r = self.delete(f"/hide_version/{doc_v1['version_id']}")
        assert r.status_code == 200

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

    def test_dot_not_hide_last(self):

        self.add_user(roles="moderator")
        self.login_user()

        doc_v1 = self.put_document(data="v1").json["document"]
        r = self.put(f"/hide_version/{doc_v1['version_id']}")
        assert r.status_code == 400

        doc_v2 = self.post_document(doc_v1["id"], data="v2").json["document"]
        r = self.put(f"/hide_version/{doc_v1['version_id']}")
        assert r.status_code == 200

        r = self.put(f"/hide_version/{doc_v2['version_id']}")
        assert r.status_code == 400
