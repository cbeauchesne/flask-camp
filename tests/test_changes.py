from tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_main(self, client):
        r = client.get("/changes")
        assert r.status_code == 200
        assert r.json["changes"] == []

    def test_simple(self, client):
        user = self.add_user()
        self.login_user(client)

        doc1 = client.put("/documents", json={"document": {"namespace": "x", "value": "doc_1/v1"}}).json["document"]
        doc2 = client.put("/documents", json={"document": {"namespace": "x", "value": "doc_2/v1"}}).json["document"]

        client.post(f"/document/{doc1['id']}", json={"document": {"namespace": "x", "value": "doc_1/v2"}})
        client.post(f"/document/{doc2['id']}", json={"document": {"namespace": "x", "value": "doc_2/v2"}})

        r = client.get("/changes", query_string={"id": doc1["id"]})
        assert r.status_code == 200, r.json
        history = r.json
        assert history["count"] == len(history["changes"]) == 2
        assert history["changes"][0]["version_id"] > history["changes"][1]["version_id"]
        assert history["changes"][0]["timestamp"] > history["changes"][1]["timestamp"]
        assert history["changes"][0]["id"] == history["changes"][1]["id"] == doc1["id"]
        assert history["changes"][0]["data"] == {"value": "doc_1/v2"}
        assert history["changes"][1]["data"] == {"value": "doc_1/v1"}

    def test_user_filter(self, client):
        user_1 = self.add_user()
        user_2 = self.add_user("user2")

        self.login_user(client)
        doc = client.put("/documents", json={"document": {"namespace": "x", "value": f"x"}}).json["document"]
        client.post(f"/document/{doc['id']}", json={"document": {"namespace": "x", "value": "y"}})
        client.get("/logout")

        self.login_user(client, "user2")
        doc = client.put("/documents", json={"document": {"namespace": "x", "value": f"x"}}).json["document"]
        client.post(f"/document/{doc['id']}", json={"document": {"namespace": "x", "value": "y"}})
        client.get("/logout")

        r = client.get("/changes", query_string={"user_id": user_1.id})
        assert r.status_code == 200, r.json
        history = r.json
        assert history["count"] == len(history["changes"]) == 2
