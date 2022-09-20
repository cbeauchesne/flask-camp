from tests.utils import BaseTest


class Test_Documents(BaseTest):
    def test_basic(self, user):
        self.login_user(user)

        r = self.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 0
        assert r.json["documents"] == []

        self.create_document(data={"value": "42"})

        r = self.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 1
        assert len(r.json["documents"]) == 1
        assert r.json["documents"][0]["data"] == {"value": "42"}

        self.create_document()
        r = self.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 2
        assert len(r.json["documents"]) == 2

    def test_offset_limit(self, user):
        self.login_user(user)

        for i in range(110):
            r = self.create_document(data={"value": f"doc {i}"}, expected_status=200)

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

        r = self.get("/versions").json
        assert r["count"] == 110
        assert len(r["versions"]) == 30

        r = self.get("/versions", query_string={"limit": 1}).json
        assert len(r["versions"]) == 1

        r = self.get("/versions", query_string={"limit": 101})
        assert r.status_code == 400
