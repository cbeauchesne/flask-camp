from cms.database import database


class Test_DocumentCreation:
    def test_simple(self, client):
        r = client.put("/documents", json={"document": {"namespace": "template", "value": "42"}})
        assert r.status_code == 200
        assert r.json["status"] == "ok"

        document = r.json["document"]

        print(document)

        assert document["comment"] == "creation"
        assert str(document["data"]) == '{"value": "42"}'
        assert isinstance(document["id"], int)
        assert document["timestamp"] is not None
        assert isinstance(document["version_id"], int)
        # assert document["author_id"] is not None
