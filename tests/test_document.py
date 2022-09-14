import json
from tests.utils import BaseTest


class Test_Document(BaseTest):
    def assert_document(self, document, user, data, comment="creation"):
        assert document["comment"] == comment
        assert document["namespace"] == "x"
        assert json.dumps(document["data"]) == json.dumps(data)
        assert isinstance(document["id"], int)
        assert isinstance(document["timestamp"], str)
        assert isinstance(document["version_id"], int)
        assert document["user"]["id"] == user.id

    def test_errors(self):
        self.create_document(expected_status=403)  # not logged

        self.db_add_user()
        self.login_user()

        self.get_document(1, expected_status=404)
        self.modify_document(1, expected_status=404)

        r = self.put("/documents", json={"document": {"data": {}}})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "'namespace' is a required property on instance ['document']"

        r = self.put("/documents", json={"document": {"namespace": "x"}})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "'data' is a required property on instance ['document']"

    def test_creation(self):
        user = self.db_add_user()
        self.login_user()

        r = self.create_document(data={"value": "42"})
        self.assert_document(r.json["document"], user, data={"value": "42"})

        document_id = r.json["document"]["id"]

        r = self.get_document(document_id)
        self.assert_document(r.json["document"], user, data={"value": "42"})

    def test_modification(self):
        user = self.db_add_user()
        self.login_user()

        v1 = self.create_document(expected_status=200).json["document"]
        v2 = self.modify_document(v1, data={"value": "43"}, expected_status=200).json["document"]

        self.assert_document(v2, user, comment="", data={"value": "43"})

        r = self.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 1
        assert r.json["documents"][0]["version_id"] == v2["version_id"]

    def test_deletion_error(self):
        self.delete_document(1, expected_status=403)

        self.db_add_user(roles="admin")
        self.login_user()

        self.delete_document(1, expected_status=404)

    def test_deletion(self):
        self.db_add_user(roles="admin")
        self.login_user()

        doc = self.create_document().json["document"]
        self.delete_document(doc, expected_status=200)
        self.get_document(doc, expected_status=404)
        self.get_document_version(doc, expected_status=404)
