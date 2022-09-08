from tests.utils import BaseTest


class Test_Documents(BaseTest):
    def test_simple(self):
        self.add_user()
        self.login_user()

        for i in range(110):
            r = self.put("/documents", json={"document": {"namespace": "x", "value": f"doc {i}"}})
            assert r.status_code == 200

        r = self.get("/documents").json
        assert r["count"] == 110
        assert len(r["documents"]) == 30

        r = self.get("/documents", query_string={"limit": 1}).json
        assert len(r["documents"]) == 1

        r = self.get("/documents", query_string={"limit": 0}).json
        assert len(r["documents"]) == 0

        r = self.get("/documents", query_string={"limit": 100}).json
        assert len(r["documents"]) == 100

        r = self.get("/documents", query_string={"limit": 101})
        assert r.status_code == 400

        r = self.get("/documents", query_string={"limit": "nan"}).json
        assert len(r["documents"]) == 30

        r = self.get("/documents").json
        assert r["documents"][0]["data"]["value"] == "doc 0"
        assert r["documents"][29]["data"]["value"] == "doc 29"

        r = self.get("/documents", query_string={"offset": 30}).json
        assert r["documents"][0]["data"]["value"] == "doc 30"
        assert r["documents"][29]["data"]["value"] == "doc 59"

        r = self.get("/changes").json
        assert r["count"] == 110
        assert len(r["changes"]) == 30

        r = self.get("/changes", query_string={"limit": 1}).json
        assert len(r["changes"]) == 1

        r = self.get("/changes", query_string={"limit": 101})
        assert r.status_code == 400
