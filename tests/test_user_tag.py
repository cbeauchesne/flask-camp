# request tags
# get changes on document with some tag
# get changes on document with some tag value
# get changes on document with some tag for user X
# get changes on document with some tag value for user X

from tests.utils import BaseTest


def assert_tag(tag, user, document_id, name, value):
    assert len(tag) == 4
    assert tag["user_id"] == user.id, tag
    assert tag["document_id"] == document_id, tag
    assert tag["name"] == name, tag
    assert tag["value"] == value, tag


class Test_UserTag(BaseTest):
    def test_not_anonymous(self):
        r = self.post("/user_tags")
        assert r.status_code == 403

    def test_add_modify_delete(self):
        user = self.add_user()
        self.login_user()

        doc = self.put_document().json["document"]

        r = self.post("/user_tags", json={"name": "x", "document_id": doc["id"]})
        assert r.status_code == 200
        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "x", None)

        r = self.post("/user_tags", json={"name": "y", "document_id": doc["id"], "value": "6a"})
        assert r.status_code == 200
        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "x", None)
        assert_tag(r.json["user_tags"][1], user, doc["id"], "y", "6a")

        r = self.post("/user_tags", json={"name": "x", "document_id": doc["id"], "value": "6b"})
        assert r.status_code == 200
        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "x", "6b")
        assert_tag(r.json["user_tags"][1], user, doc["id"], "y", "6a")

        r = self.delete("/user_tags", json={"name": "x", "document_id": doc["id"]})
        assert r.status_code == 200
        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "y", "6a")

    def test_get_tags(self):
        #   filter on user id
        #   filter on documemt id
        #   filter on tag name
        #   filter on tag name and value
        pass

    def test_get_documents(self):
        # get documents with some tag
        # get documents with some tag value
        # get documents with some tag for user X
        # get documents with some tag value for user X
        pass
