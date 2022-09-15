from tests.utils import BaseTest


class Test_GetVersion(BaseTest):
    def test_errors(self):
        r = self.get("/document_version/42")
        assert r.status_code == 404

    def test_main(self):
        self.db_add_user()
        self.login_user()

        v0 = self.create_document().json["document"]
        v1 = self.modify_document(v0, data={"value": "43"}).json["document"]

        self.logout_user()

        r = self.get(f"/document_version/{v0['version_id']}")
        assert r.status_code == 200
        assert r.json["document"]["data"] == {}

        r = self.get(f"/document_version/{v1['version_id']}")
        assert r.status_code == 200
        assert r.json["document"]["data"] == {"value": "43"}

        modo = self.db_add_user("modo", roles="moderator")
        self.login_user(modo.name)

        self.hide_version(v0)

        r = self.get(f"/document_version/{v0['version_id']}")
        assert r.status_code == 200
        assert r.json["document"]["data"] == {}

        self.login_user()

        r = self.get(f"/document_version/{v0['version_id']}")
        assert r.status_code == 200
        assert "data" not in r.json["document"]
        assert r.json["document"]["hidden"] is True


class Test_DeleteVersion(BaseTest):
    def test_main(self):
        self.db_add_user()
        admin = self.db_add_user("admin", roles="admin")
        self.login_user()

        v0 = self.create_document().json["document"]
        document_id = v0["id"]

        v1 = self.modify_document(v0, data={"value": "43"}).json["document"]
        self.modify_document(v1, data={"value": "43"})

        r = self.get("/document_versions", query_string={"document_id": document_id})
        assert r.json["count"] == 3

        self.logout_user()
        self.login_user(admin.name)

        self.delete_document_version(v1, expected_status=200)

        r = self.get("/document_versions", query_string={"document_id": document_id})
        assert r.json["count"] == 2

    def test_not_the_last_one(self):
        self.db_add_user(roles="admin")
        self.login_user()

        v0 = self.create_document().json["document"]
        r = self.delete_document_version(v0, expected_status=400)
        assert r.json["description"] == "Can't delete last version of a document"

    def test_rights(self):
        self.db_add_user()
        self.login_user()

        v0 = self.create_document().json["document"]
        self.delete_document_version(v0, expected_status=403)

    def test_not_found(self):
        self.db_add_user(roles="admin")
        self.login_user()

        self.delete_document_version(42, expected_status=404)

    def test_bad_format(self):
        self.db_add_user(roles="admin")
        self.login_user()

        r = self.delete("/document_version/200", json={"commentt": "toto"})
        assert r.status_code == 400, r.json

        r = self.delete("/document_version/200")
        assert r.status_code == 400, r.json
