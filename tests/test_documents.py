import json
from tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_creation_not_logged(self):
        r = self.put_document()
        assert r.status_code == 403

    def assert_document(self, document, user, data, comment="creation"):
        assert document["comment"] == comment
        assert document["namespace"] == "x"
        assert json.dumps(document["data"]) == json.dumps(data)
        assert isinstance(document["id"], int)
        assert isinstance(document["timestamp"], str)
        assert isinstance(document["version_id"], int)
        assert document["user"]["id"] == user.id

    def test_creation(self):
        user = self.add_user()
        self.login_user()

        r = self.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 0
        assert r.json["documents"] == []

        r = self.put_document(data={"value": "42"})
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        self.assert_document(r.json["document"], user, data={"value": "42"})

        document_id = r.json["document"]["id"]

        r = self.get(f"/document/{document_id}")
        assert r.json["status"] == "ok"
        self.assert_document(r.json["document"], user, data={"value": "42"})

        r = self.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 1
        assert len(r.json["documents"]) == 1

        self.assert_document(r.json["documents"][0], user, data={"value": "42"})

    def test_modification(self):
        user = self.add_user()
        self.login_user()

        r = self.put_document()
        assert r.status_code == 200, r.json
        first_version = r.json["document"]
        document_id = first_version["id"]

        r = self.post_document(document_id, data={"value": "43"})
        assert r.status_code == 200
        second_version = r.json["document"]

        self.assert_document(second_version, user, comment="", data={"value": "43"})

        r = self.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 1
        assert r.json["documents"][0]["version_id"] == second_version["version_id"]

    def test_errors(self):
        self.add_user()
        self.login_user()

        r = self.get("/document/1")
        assert r.status_code == 404

        r = self.post_document(1)
        assert r.status_code == 404

        r = self.put("/documents", json={"document": {"data": {}}})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "'namespace' is a required property on instance ['document']"

        r = self.put("/documents", json={"document": {"namespace": "x"}})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "'data' is a required property on instance ['document']"
