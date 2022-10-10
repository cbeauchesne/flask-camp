from tests.unit_tests.utils import BaseTest


class Test_CustomSearch(BaseTest):
    def test_main(self, admin):
        self.login_user(admin)
        self.add_user_role(admin, "moderator", "I'am god")

        doc_1 = self.create_document(data={"type": "x"}).json["document"]
        doc_2 = self.create_document(data={"type": ""}).json["document"]

        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_1["id"]

        self.delete_document(doc_1)
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 0

        doc_2_v2 = self.modify_document(doc_2, data={"type": "x"}).json["document"]
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_2["id"]

        self.hide_version(doc_2_v2)
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 0

        self.unhide_version(doc_2_v2)
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_2["id"]

        self.delete_version(doc_2_v2)
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 0

    #     # merge
