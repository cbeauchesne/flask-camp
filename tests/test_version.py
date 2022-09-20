from tests.utils import BaseTest


class Test_GetVersion(BaseTest):
    def test_errors(self):
        r = self.get("/version/42")
        assert r.status_code == 404

    def test_main(self, user, moderator):
        self.login_user(user)

        v0 = self.create_document().json["document"]
        v1 = self.modify_document(v0, data={"value": "43"}).json["document"]

        self.logout_user()

        r = self.get(f"/version/{v0['version_id']}")
        assert r.status_code == 200
        assert r.json["document"]["data"] == {}

        r = self.get(f"/version/{v1['version_id']}")
        assert r.status_code == 200
        assert r.json["document"]["data"] == {"value": "43"}

        self.login_user(moderator)

        self.hide_version(v0)

        r = self.get(f"/version/{v0['version_id']}")
        assert r.status_code == 200
        assert r.json["document"]["data"] == {}

        self.login_user(user)

        r = self.get(f"/version/{v0['version_id']}")
        assert r.status_code == 200
        assert "data" not in r.json["document"]
        assert r.json["document"]["hidden"] is True


class Test_DeleteVersion(BaseTest):
    def test_main(self, admin):
        self.login_user(admin)

        v0 = self.create_document().json["document"]
        document_id = v0["id"]

        v1 = self.modify_document(v0, data={"value": "43"}).json["document"]
        self.modify_document(v1, data={"value": "43"})

        r = self.get("/versions", query_string={"document_id": document_id})
        assert r.json["count"] == 3

        self.logout_user()
        self.login_user(admin)

        self.delete_document_version(v1, expected_status=200)

        r = self.get("/versions", query_string={"document_id": document_id})
        assert r.json["count"] == 2

    def test_not_the_last_one(self, admin):
        self.login_user(admin)

        v0 = self.create_document().json["document"]
        r = self.delete_document_version(v0, expected_status=400)
        assert r.json["description"] == "Can't delete last version of a document"

    def test_rights(self, user):
        self.login_user(user)

        v0 = self.create_document().json["document"]
        self.delete_document_version(v0, expected_status=403)

    def test_not_found(self, admin):
        self.login_user(admin)

        self.delete_document_version(42, expected_status=404)

    def test_bad_format(self, admin):
        self.login_user(admin)

        r = self.delete("/version/200", json={"commentt": "toto"})
        assert r.status_code == 400, r.json

        r = self.delete("/version/200")
        assert r.status_code == 400, r.json
