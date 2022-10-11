from tests.unit_tests.utils import BaseTest


def cooker(document, get_document):  # pylint: disable=unused-argument
    data = document.get("data")

    if isinstance(data, dict):
        document["cooked"] = True


class Test_Merge(BaseTest):
    rest_api_kwargs = {"cooker": cooker}

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

    def test_no_comment(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document().json["document"]
        doc_2 = self.create_document().json["document"]

        self.merge_documents(document_to_merge=doc_1, document_destination=doc_2, comment=None, expected_status=400)

    def test_do_not_see_merged_document(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document().json["document"]
        doc_2 = self.create_document().json["document"]

        self.merge_documents(document_to_merge=doc_1, document_destination=doc_2, comment="merged")

        r = self.get_documents().json

        assert r["count"] == 1
        assert r["documents"][0]["id"] == doc_2["id"], r["documents"][0]

    def test_dont_modify_redirection(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document().json["document"]
        doc_2 = self.create_document().json["document"]

        self.merge_documents(document_to_merge=doc_1, document_destination=doc_2, comment="merged")

        self.modify_document(doc_1, expected_status=400)

    def test_dont_cook_redirections(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document(data={"namespace": "cook-me"}).json["document"]
        doc_2 = self.create_document(data={"namespace": "cook-me"}).json["document"]

        self.merge_documents(document_to_merge=doc_1, document_destination=doc_2, comment="merged")

        doc_1 = self.get_document(doc_1, expected_status=301).json["document"]
        doc_2 = self.get_document(doc_2).json["document"]

        assert "cooked" not in doc_1
        assert "cooked" in doc_2

    def test_merge_redirections(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document().json["document"]
        doc_2 = self.create_document().json["document"]
        doc_3 = self.create_document().json["document"]

        self.merge_documents(doc_1, doc_2, comment="Doc 1 is now a redirection")

        self.merge_documents(doc_1, doc_3, comment="nope", expected_status=400)
        self.merge_documents(doc_3, doc_1, comment="nope", expected_status=400)
