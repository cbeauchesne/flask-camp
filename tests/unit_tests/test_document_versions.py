from tests.unit_tests.utils import BaseTest


class Test_DocumentVersions(BaseTest):
    def test_main(self):
        r = self.get_versions(expected_status=200)
        assert r.json["versions"] == []

    def test_simple(self, user):
        self.login_user(user)

        doc1 = self.create_document(data={"value": "doc_1/v1"}).json["document"]
        doc2 = self.create_document(data={"value": "doc_2/v1"}).json["document"]

        self.modify_document(doc1, data={"value": "doc_1/v2"})
        self.modify_document(doc2, data={"value": "doc_2/v2"})

        r = self.get_versions(document=doc1, expected_status=200)
        history = r.json
        assert history["count"] == len(history["versions"]) == 2
        assert history["versions"][0]["version_id"] > history["versions"][1]["version_id"]
        assert history["versions"][0]["timestamp"] > history["versions"][1]["timestamp"]
        assert history["versions"][0]["id"] == history["versions"][1]["id"] == doc1["id"]
        assert history["versions"][0]["data"] == {"value": "doc_1/v2"}
        assert history["versions"][1]["data"] == {"value": "doc_1/v1"}

    def test_user_filter(self, user, user_2):

        self.login_user(user)
        doc = self.create_document(data={"value": "x"}).json["document"]
        self.modify_document(doc, data={"value": "y"})
        self.logout_user()

        self.login_user(user_2)
        doc = self.create_document(data={"value": "x"}).json["document"]
        self.modify_document(doc, data={"value": "y"})
        self.logout_user()

        r = self.get_versions(user=user, expected_status=200)

        history = r.json
        assert history["count"] == len(history["versions"]) == 2

    def test_user_tag_filter(self, user, user_2):
        self.login_user(user)
        doc1 = self.create_document().json["document"]
        doc2 = self.create_document().json["document"]
        self.add_user_tag("follow_list", doc1)
        self.logout_user()

        self.login_user(user_2)
        doc3 = self.create_document().json["document"]
        self.add_user_tag("follow_list", doc2)
        self.add_user_tag("other", doc3)
        self.logout_user()

        r = self.get_versions()
        assert r.json["count"] == 3

        r = self.get_versions(tag_name="follow_list")
        assert r.json["count"] == 2

        r = self.get_versions(tag_name="follow_list", tag_user=user)
        assert r.json["count"] == 1
        assert r.json["versions"][0]["id"] == doc1["id"]

        r = self.get_versions(tag_name="follow_list", tag_user=user_2)
        assert r.json["count"] == 1
        assert r.json["versions"][0]["id"] == doc2["id"]
