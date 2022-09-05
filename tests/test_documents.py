from tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_creation_not_logged(self, client):
        r = client.put("/documents", json={"document": {"namespace": "template", "value": "42"}})
        assert r.status_code == 401

    def assert_document(self, document, author, comment="creation", data='{"value": "42"}'):
        assert document["comment"] == comment
        assert document["namespace"] == "template"
        assert str(document["data"]) == data
        assert isinstance(document["id"], int)
        assert isinstance(document["timestamp"], str)
        assert isinstance(document["version_id"], int)
        assert document["author"]["id"] == author.id

    def test_creation(self, client):
        user = self.add_user()
        self.login_user(client)

        r = client.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 0
        assert r.json["documents"] == []

        r = client.put("/documents", json={"document": {"namespace": "template", "value": "42"}})
        assert r.status_code == 200
        assert r.json["status"] == "ok"

        document = r.json["document"]

        self.assert_document(r.json["document"], user)

        document_id = document["id"]
        r = client.get(f"/document/{document_id}")
        assert r.json["status"] == "ok"
        self.assert_document(r.json["document"], user)

        r = client.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 1
        assert len(r.json["documents"]) == 1

        self.assert_document(r.json["documents"][0], user)

    def test_modification(self, client):
        user = self.add_user()
        self.login_user(client)

        r = client.put("/documents", json={"document": {"namespace": "template", "value": "42"}})
        assert r.status_code == 200, r.json
        first_version = r.json["document"]
        document_id = first_version["id"]

        r = client.post(f"/document/{document_id}", json={"document": {"namespace": "template", "value": "43"}})
        assert r.status_code == 200
        second_version = r.json["document"]

        self.assert_document(second_version, user, comment="", data='{"value": "43"}')

        r = client.get("documents")
        assert r.status_code == 200
        assert r.json["status"] == "ok"
        assert r.json["count"] == 1
        assert r.json["documents"][0]["version_id"] == second_version["version_id"]
