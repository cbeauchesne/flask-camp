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

    def test_add_modify_delete(self, user):
        self.login_user(user)

        doc = self.create_document().json["document"]

        self.add_user_tag("x", doc, expected_status=200)

        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "x", None)

        self.add_user_tag("y", doc, "6a", expected_status=200)

        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "x", None)
        assert_tag(r.json["user_tags"][1], user, doc["id"], "y", "6a")

        r = self.add_user_tag("x", doc, "6b")
        assert r.status_code == 200
        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "x", "6b")
        assert_tag(r.json["user_tags"][1], user, doc["id"], "y", "6a")

        r = self.remove_user_tag("x", doc, expected_status=200)

        r = self.get("/user_tags")
        assert_tag(r.json["user_tags"][0], user, doc["id"], "y", "6a")

    def test_get_tags(self, user, user_2):

        self.login_user(user)
        doc1 = self.create_document().json["document"]
        doc2 = self.create_document().json["document"]

        self.add_user_tag("t1", doc1)
        self.add_user_tag("t2", doc1)
        self.add_user_tag("t1", doc2)
        self.add_user_tag("t2", doc2)

        self.logout_user()
        self.login_user(user_2)

        self.add_user_tag("t1", doc1)
        self.add_user_tag("t2", doc1)
        self.add_user_tag("t1", doc2)
        self.add_user_tag("t2", doc2)

        r = self.get("/user_tags")
        assert r.json["count"] == 8

        r = self.get("/user_tags", query_string={"user_id": user.id})
        assert r.json["count"] == 4

        r = self.get("/user_tags", query_string={"document_id": doc1["id"]})
        assert r.json["count"] == 4

        r = self.get("/user_tags", query_string={"name": "t1"})
        assert r.json["count"] == 4

        r = self.get("/user_tags", query_string={"user_id": user.id, "document_id": doc1["id"]})
        assert r.json["count"] == 2

        r = self.get("/user_tags", query_string={"document_id": doc1["id"], "name": "t1"})
        assert r.json["count"] == 2

        r = self.get("/user_tags", query_string={"user_id": user.id, "name": "t1"})
        assert r.json["count"] == 2

        r = self.get("/user_tags", query_string={"user_id": user.id, "document_id": doc1["id"], "name": "t1"})
        assert r.json["count"] == 1

    def test_get_documents(self, user, user_2):
        self.login_user(user)
        doc1 = self.create_document().json["document"]
        doc2 = self.create_document().json["document"]
        doc3 = self.create_document().json["document"]

        self.add_user_tag("t1", doc1, "6a")
        self.add_user_tag("t1", doc2)
        self.add_user_tag("t2", doc3)

        self.logout_user()

        self.login_user(user_2)
        self.add_user_tag("t1", doc1)

        r = self.get("/documents", query_string={"tag_name": "t1"})
        assert r.json["count"] == 2

        r = self.get("/documents", query_string={"tag_name": "t1", "tag_user_id": user_2.id})
        assert r.json["count"] == 1

        r = self.get("/documents", query_string={"tag_name": "t1", "tag_value": "6a"})
        assert r.json["count"] == 1

    def test_errors(self, user):
        self.login_user(user)

        doc = self.create_document().json["document"]

        r = self.delete("/user_tags", json={"name": "x", "document_id": doc["id"]})
        assert r.status_code == 404

        r = self.get("/user_tags", query_string={"limit": 101})
        assert r.status_code == 400
