# request tags
# get changes on document with some tag
# get changes on document with some tag value
# get changes on document with some tag for user X
# get changes on document with some tag value for user X

from tests.utils import BaseTest


class Test_UserTag(BaseTest):
    def test_not_anonymous(self):
        r = self.post("/user_tags")
        assert r.status_code == 403

    def test_add_modify_delete(self):
        self.add_user()
        self.login_user()

        doc = self.put_document().json["document"]

        r = self.post("/user_tags", json={"name": "x", "document_id": doc["id"]})
        assert r.status_code == 200
        r = self.post("/user_tags", json={"name": "y", "document_id": doc["id"], "value": "6a"})
        assert r.status_code == 200
        r = self.post("/user_tags", json={"name": "x", "document_id": doc["id"], "value": "6a"})
        assert r.status_code == 200
        r = self.delete("/user_tags", json={"name": "x", "document_id": doc["id"]})
        assert r.status_code == 200

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
