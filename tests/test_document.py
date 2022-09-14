from tests.utils import BaseTest


class Test_Document(BaseTest):
    def delete_document(self, document, expected_status=200):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.delete(f"/document/{document_id}", json={"comment": "comment"})
        assert r.status_code == expected_status, r.json

        return r

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
