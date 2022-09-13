from tests.utils import BaseTest


class Test_DeleteVersion(BaseTest):
    def test_main(self):
        self.add_user()
        admin = self.add_user("admin", roles="admin")
        self.login_user()

        v0 = self.put_document().json["document"]
        document_id = v0["id"]

        v1 = self.post_document(document_id, data={"value": "43"}).json["document"]
        self.post_document(document_id, data={"value": "43"})

        r = self.get("/changes", query_string={"document_id": v0["id"]})
        assert r.json["count"] == 3

        self.logout_user()
        self.login_user(admin.name)

        r = self.delete(f"/document_version/{v1['id']}", json={"comment": "toto"})
        assert r.status_code == 200, r.json

        r = self.get("/changes", query_string={"document_id": v0["id"]})
        assert r.json["count"] == 2

    def test_not_the_last_one(self):
        self.add_user(roles="admin")
        self.login_user()

        v0 = self.put_document().json["document"]
        r = self.delete(f"/document_version/{v0['id']}", json={"comment": "toto"})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "Can't delete last version of a document"

    def test_rights(self):
        self.add_user()
        self.login_user()

        v0 = self.put_document().json["document"]
        r = self.delete(f"/document_version/{v0['id']}", json={"comment": "toto"})
        assert r.status_code == 403, r.json

    def test_not_found(self):
        self.add_user(roles="admin")
        self.login_user()

        r = self.delete("/document_version/200", json={"comment": "toto"})
        assert r.status_code == 404, r.json

    def test_bad_format(self):
        self.add_user(roles="admin")
        self.login_user()

        r = self.delete("/document_version/200", json={"commentt": "toto"})
        assert r.status_code == 400, r.json

        r = self.delete("/document_version/200")
        assert r.status_code == 400, r.json

        r = self.delete("/document_version/200", json={"commentt": "toto", "comment": "toto"})
        assert r.status_code == 400, r.json
