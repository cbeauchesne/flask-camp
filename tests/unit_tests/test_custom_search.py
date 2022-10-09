from tests.unit_tests.utils import BaseTest


class Test_CustomSearch(BaseTest):
    def test_main(self, admin):
        self.login_user(admin)

        doc = self.create_document(data={"namespace": "x"}).json["document"]
        self.create_document(data={"namespace": ""})

        documents = self.get_documents(params={"namespace": "x"}).json["documents"]

        assert len(documents) == 1
        assert documents[0]["id"] == doc["id"]

        self.delete_document(doc)
        documents = self.get_documents(params={"namespace": "x"}).json["documents"]

        assert len(documents) == 0

    #     # lot of use case to test
    #     # update
    #     # hide version
    #     # delete version
    #     # merge
