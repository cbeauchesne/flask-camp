from tests.unit_tests.utils import BaseTest


class Test_Merge(BaseTest):
    def test_main(self, moderator, admin):
        self.login_user(moderator)

        v1 = self.create_document(data="v1").json["document"]
        v2 = self.create_document(data="v2").json["document"]

        v3 = self.modify_document(v1, data="v3").json["document"]
        v4 = self.modify_document(v2, data="v4").json["document"]

        doc = self.get_document(v1).json["document"]
        assert doc["id"] == v1["id"]

        self.merge_documents(document_to_merge=v1, document_destination=v2, comment="test")

        versions = self.get_versions(document=v2).json["versions"]
        versions = self.get_versions().json["versions"]

        assert len(versions) == 4

        assert versions[0]["timestamp"] > versions[1]["timestamp"] > versions[2]["timestamp"] > versions[3]["timestamp"]

        assert versions[0]["version_id"] == v4["version_id"]
        assert versions[1]["version_id"] == v3["version_id"]
        assert versions[2]["version_id"] == v2["version_id"]
        assert versions[3]["version_id"] == v1["version_id"]

        r = self.get_document(v1, expected_status=301)
        assert r.headers["Location"] == f"/document/{v2['id']}"

        self.modify_document(v1, data="v3", expected_status=400)
        self.modify_document(v3, data="v3", expected_status=400)

        self.protect_document(v1, expected_status=400)
        self.unprotect_document(v1, expected_status=400)

        self.logout_user()
        self.login_user(admin)

        self.delete_document(v1, expected_status=200)

    def test_forbidden(self, user):
        self.login_user(user)

        v1 = self.create_document(data="v1").json["document"]
        v2 = self.create_document(data="v2").json["document"]

        self.merge_documents(document_to_merge=v1, document_destination=v2, comment="test", expected_status=403)

    def test_common_doc(self, moderator):
        self.login_user(moderator)

        v1 = self.create_document(data="v1").json["document"]

        self.merge_documents(document_to_merge=v1, document_destination=v1, comment="test", expected_status=400)
        self.merge_documents(document_to_merge=v1, document_destination={"id": 42}, comment="test", expected_status=404)

    def test_malformatted(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document().json["document"]
        doc_2 = self.create_document().json["document"]

        self.merge_documents(document_to_merge=doc_1, document_destination=doc_2, expected_status=400)


# TODO : test modify a redirection
