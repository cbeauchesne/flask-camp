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
        user1 = self.add_user("user1")
        user2 = self.add_user("user2")

        self.login_user(user1.name)
        doc1 = self.put_document().json["document"]
        doc2 = self.put_document().json["document"]

        self.post("/user_tags", json={"name": "t1", "document_id": doc1["id"]})
        self.post("/user_tags", json={"name": "t2", "document_id": doc1["id"]})
        self.post("/user_tags", json={"name": "t1", "document_id": doc2["id"]})
        self.post("/user_tags", json={"name": "t2", "document_id": doc2["id"]})

        self.logout_user()
        self.login_user(user2.name)

        self.post("/user_tags", json={"name": "t1", "document_id": doc1["id"]})
        self.post("/user_tags", json={"name": "t2", "document_id": doc1["id"]})
        self.post("/user_tags", json={"name": "t1", "document_id": doc2["id"]})
        self.post("/user_tags", json={"name": "t2", "document_id": doc2["id"]})

        r = self.get("/user_tags")
        assert r.json["count"] == 8

        r = self.get("/user_tags", query_string={"user_id": user1.id})
        assert r.json["count"] == 4

        r = self.get("/user_tags", query_string={"document_id": doc1["id"]})
        assert r.json["count"] == 4

        r = self.get("/user_tags", query_string={"name": "t1"})
        assert r.json["count"] == 4

        r = self.get("/user_tags", query_string={"user_id": user1.id, "document_id": doc1["id"]})
        assert r.json["count"] == 2

        r = self.get("/user_tags", query_string={"document_id": doc1["id"], "name": "t1"})
        assert r.json["count"] == 2

        r = self.get("/user_tags", query_string={"user_id": user1.id, "name": "t1"})
        assert r.json["count"] == 2

        r = self.get("/user_tags", query_string={"user_id": user1.id, "document_id": doc1["id"], "name": "t1"})
        assert r.json["count"] == 1

    def test_get_documents(self):

        # # get all doc that have at least a tag t1
        # r = self.get("/documents", query_string={"tag_name": "t1"})

        # # get all doc that have at least a tag t1   
        # r = self.get("/documents", query_string={"tag_name": "t1", "tag_value": "6a"})

        # # get all doc that have at least a tag t1 for user id 1
        # r = self.get("/documents", query_string={"tag_name": "t1", "tag_user_id": 1})
        pass

    def test_errors(self):
        self.add_user()
        self.login_user()

        doc = self.put_document().json["document"]

        r = self.delete("/user_tags", json={"name": "x", "document_id": doc["id"]})
        assert r.status_code == 404

        r = self.get("/user_tags", query_string={"limit": 101})
        assert r.status_code == 400