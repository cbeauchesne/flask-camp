from tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_main(self):
        r = self.get("/changes")
        assert r.status_code == 200
        assert r.json["changes"] == []

    def test_simple(self):
        user = self.add_user()
        self.login_user()

        doc1 = self.put("/documents", json={"document": {"namespace": "x", "value": "doc_1/v1"}}).json["document"]
        doc2 = self.put("/documents", json={"document": {"namespace": "x", "value": "doc_2/v1"}}).json["document"]

        self.post(f"/document/{doc1['id']}", json={"document": {"namespace": "x", "value": "doc_1/v2"}})
        self.post(f"/document/{doc2['id']}", json={"document": {"namespace": "x", "value": "doc_2/v2"}})

        r = self.get("/changes", query_string={"id": doc1["id"]})
        assert r.status_code == 200, r.json
        history = r.json
        assert history["count"] == len(history["changes"]) == 2
        assert history["changes"][0]["version_id"] > history["changes"][1]["version_id"]
        assert history["changes"][0]["timestamp"] > history["changes"][1]["timestamp"]
        assert history["changes"][0]["id"] == history["changes"][1]["id"] == doc1["id"]
        assert history["changes"][0]["data"] == {"value": "doc_1/v2"}
        assert history["changes"][1]["data"] == {"value": "doc_1/v1"}

    def test_user_filter(self):
        user_1 = self.add_user()
        user_2 = self.add_user("user2")

        self.login_user()
        doc = self.put("/documents", json={"document": {"namespace": "x", "value": f"x"}}).json["document"]
        self.post(f"/document/{doc['id']}", json={"document": {"namespace": "x", "value": "y"}})
        self.get("/logout")

        self.login_user("user2")
        doc = self.put("/documents", json={"document": {"namespace": "x", "value": f"x"}}).json["document"]
        self.post(f"/document/{doc['id']}", json={"document": {"namespace": "x", "value": "y"}})
        self.get("/logout")

        r = self.get("/changes", query_string={"user_id": user_1.id})
        assert r.status_code == 200, r.json
        history = r.json
        assert history["count"] == len(history["changes"]) == 2
