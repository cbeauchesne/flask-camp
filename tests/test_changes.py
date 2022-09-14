from tests.utils import BaseTest


class Test_Changes(BaseTest):
    def test_main(self):
        r = self.get("/changes")
        assert r.status_code == 200
        assert r.json["changes"] == []

    def test_simple(self):
        self.db_add_user()
        self.login_user()

        doc1 = self.create_document(data={"value": "doc_1/v1"}).json["document"]
        doc2 = self.create_document(data={"value": "doc_2/v1"}).json["document"]

        self.modify_document(doc1["id"], data={"value": "doc_1/v2"})
        self.modify_document(doc2["id"], data={"value": "doc_2/v2"})

        r = self.get("/changes", query_string={"document_id": doc1["id"]})
        assert r.status_code == 200, r.json
        history = r.json
        assert history["count"] == len(history["changes"]) == 2
        assert history["changes"][0]["version_id"] > history["changes"][1]["version_id"]
        assert history["changes"][0]["timestamp"] > history["changes"][1]["timestamp"]
        assert history["changes"][0]["id"] == history["changes"][1]["id"] == doc1["id"]
        assert history["changes"][0]["data"] == {"value": "doc_1/v2"}
        assert history["changes"][1]["data"] == {"value": "doc_1/v1"}

    def test_user_filter(self):
        user_1 = self.db_add_user()
        user_2 = self.db_add_user("user2")

        self.login_user()
        doc = self.create_document(data={"value": "x"}).json["document"]
        self.modify_document(doc["id"], data={"value": "y"})
        self.logout_user()

        self.login_user(user_2.name)
        doc = self.create_document(data={"value": "x"}).json["document"]
        self.modify_document(doc["id"], data={"value": "y"})
        self.logout_user()

        r = self.get("/changes", query_string={"user_id": user_1.id})
        assert r.status_code == 200, r.json
        history = r.json
        assert history["count"] == len(history["changes"]) == 2
