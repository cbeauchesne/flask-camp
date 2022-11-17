from sqlalchemy.orm.attributes import flag_modified
from flask_camp import current_api
from flask_camp.models import Document
from tests.unit_tests.utils import BaseTest


def before_create_document(document):
    document.data = {"views": 0}


def after_get_document(response):
    document_id = response.data["document"]["id"]
    document = Document.get(id=document_id, with_for_update=True)
    document.data["views"] += 1
    flag_modified(document, "data")
    current_api.memory_cache.delete_document(document_id)
    current_api.database.session.commit()


class Test_DocumentData(BaseTest):
    rest_api_decorated = {"before_create_document": before_create_document, "after_get_document": after_get_document}

    def test_main(self, user):
        self.login_user(user)

        document_id = self.create_document().json["document"]["id"]

        doc = self.get_document(document_id).json["document"]
        assert doc["metadata"]["views"] == 0

        doc = self.get_document(document_id).json["document"]
        assert doc["metadata"]["views"] == 1
