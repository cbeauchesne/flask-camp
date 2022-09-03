from tests.utils import BaseTest


class Test_DocumentCreation(BaseTest):
    def test_not_logged(self, client):
        r = client.put("/documents", json={"document": {"namespace": "template", "value": "42"}})
        assert r.status_code == 401

    def test_simple(self, client):
        user = self.add_user()
        self.login_user(client)

        r = client.put("/documents", json={"document": {"namespace": "template", "value": "42"}})
        assert r.status_code == 200
        assert r.json["status"] == "ok"

        document = r.json["document"]

        print(document)

        assert document["comment"] == "creation"
        # assert document["namespace"] == "template"
        assert str(document["data"]) == '{"value": "42"}'
        assert isinstance(document["id"], int)
        assert isinstance(document["timestamp"], str)
        assert isinstance(document["version_id"], int)
        assert document["author_id"] == user.id
