from tests.unit_tests.utils import BaseTest


class Test_GetVersion(BaseTest):
    def test_errors(self):
        self.get_version(42, expected_status=404)

    def test_main(self, user, moderator):
        self.login_user(user)

        v0 = self.create_document().json["document"]
        v1 = self.modify_document(v0, data={"value": "43"}).json["document"]

        self.logout_user()

        r = self.get_version(v0, expected_status=200)
        assert r.json["document"]["data"] == {}

        r = self.get_version(v1, expected_status=200)
        assert r.json["document"]["data"] == {"value": "43"}

        self.login_user(moderator)

        self.hide_version(v0)

        r = self.get_version(v0, expected_status=200)
        assert r.json["document"]["data"] == {}

        self.login_user(user)

        r = self.get_version(v0, data_should_be_present=False, expected_status=200)
        assert r.json["document"]["hidden"] is True
        assert "data" not in r.json["document"]


class Test_DeleteVersion(BaseTest):
    def test_main(self, admin):
        self.login_user(admin)

        v0 = self.create_document().json["document"]

        v1 = self.modify_document(v0, data={"value": "43"}).json["document"]
        self.modify_document(v1, data={"value": "43"})

        r = self.get_versions(document=v0)
        assert r.json["count"] == 3

        self.logout_user()
        self.login_user(admin)

        self.delete_version(v1, expected_status=200)

        r = self.get_versions(document=v0)
        assert r.json["count"] == 2

    def test_not_the_last_one(self, admin):
        self.login_user(admin)

        v0 = self.create_document().json["document"]
        r = self.delete_version(v0, expected_status=400)
        assert r.json["description"] == "Can't delete last version of a document"

    def test_rights(self, user):
        self.login_user(user)

        v0 = self.create_document().json["document"]
        self.delete_version(v0, expected_status=403)

    def test_not_found(self, admin):
        self.login_user(admin)

        self.delete_version(42, expected_status=404)

    def test_bad_format(self, admin):
        self.login_user(admin)

        self.delete("/version/200", json={"commentt": "toto"}, expected_status=400)
        self.delete("/version/200", expected_status=400)
