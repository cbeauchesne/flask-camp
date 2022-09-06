from tests.utils import BaseTest


class Test_Documents(BaseTest):
    def test_simple(self, client):
        self.add_user()
        self.login_user(client)

        for i in range(110):
            r = client.put("/documents", json={"document": {"namespace": "x", "value": f"doc {i}"}})
            assert r.status_code == 200

        r = client.get("/documents").json
        assert r["count"] == 110
        assert len(r["documents"]) == 30

        r = client.get("/documents", query_string={"limit": 1}).json
        assert len(r["documents"]) == 1

        r = client.get("/documents", query_string={"limit": 0}).json
        assert len(r["documents"]) == 0

        r = client.get("/documents", query_string={"limit": 100}).json
        assert len(r["documents"]) == 100

        r = client.get("/documents", query_string={"limit": 101})
        assert r.status_code == 400

        r = client.get("/documents", query_string={"limit": "nan"}).json
        assert len(r["documents"]) == 30

        r = client.get("/documents").json
        assert r["documents"][0]["data"]["value"] == "doc 0"
        assert r["documents"][29]["data"]["value"] == "doc 29"

        r = client.get("/documents", query_string={"offset": 30}).json
        assert r["documents"][0]["data"]["value"] == "doc 30"
        assert r["documents"][29]["data"]["value"] == "doc 59"

        r = client.get("/changes").json
        assert r["count"] == 110
        assert len(r["changes"]) == 30

        r = client.get("/changes", query_string={"limit": 1}).json
        assert len(r["changes"]) == 1

        r = client.get("/changes", query_string={"limit": 101})
        assert r.status_code == 400
