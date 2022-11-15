from flask import request
from sqlalchemy import Column, String, ForeignKey, delete
import pytest

from flask_camp import current_api
from flask_camp.models import BaseModel, Document

from tests.unit_tests.utils import BaseTest


class DocumentSearch(BaseModel):
    # Define a one-to-one relationship with document table
    # ondelete is mandatory, as a deletion of the document must delete the search item
    id = Column(ForeignKey(Document.id, ondelete="CASCADE"), index=True, nullable=True, primary_key=True)

    # We want to be able to search on a document type property
    # index is very import, obviously
    document_type = Column(String(16), index=True)


def before_create_document(document):
    search_item = DocumentSearch(id=document.id)
    current_api.database.session.add(search_item)
    update_document_search(search_item, document.last_version)


def before_update_document(document, old_version, new_version):  # pylint: disable=unused-argument
    update_document_search(DocumentSearch.get(id=document.id), new_version)


def before_merge_documents(document_to_merge, document_destination):  # pylint: disable=unused-argument
    delete(DocumentSearch).where(DocumentSearch.id == document_to_merge.id)


def update_document_search(search_item, version):
    search_item.document_type = version.data.get("type")


def update_search_query(query):
    document_type = request.args.get("t", default=None, type=str)

    if document_type is not None:
        query = query.join(DocumentSearch).where(DocumentSearch.document_type == document_type)

    return query


class Test_CustomSearch(BaseTest):
    rest_api_kwargs = {
        "update_search_query": update_search_query,
    }

    rest_api_decorated = {
        "before_create_document": before_create_document,
        "before_update_document": before_update_document,
        "before_merge_documents": before_merge_documents,
    }

    def test_main(self, admin):
        self.login_user(admin)
        self.modify_user(admin, roles=["moderator", "admin"], comment="I'am god")

        doc_1 = self.create_document(data={"type": "x"}).json["document"]
        doc_2 = self.create_document(data={"type": ""}).json["document"]

        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_1["id"]

        self.delete_document(doc_1)
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 0

        self.modify_document(doc_2, data={"type": "x"})
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_2["id"]

    @pytest.mark.xfail(reason="Can't delete/hide last version")
    def test_main_woth_delete_last_version(self, admin):
        self.login_user(admin)
        self.modify_user(admin, roles=["moderator", "admin"], comment="I'am god")

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

    def test_merge_1(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document(data={"type": "x"}).json["document"]
        doc_2 = self.create_document(data={"type": ""}).json["document"]
        self.merge_documents(doc_1, doc_2, comment="comment")
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 0

    def test_merge_2(self, moderator):
        self.login_user(moderator)

        doc_1 = self.create_document(data={"type": "x"}).json["document"]
        doc_2 = self.create_document(data={"type": ""}).json["document"]
        self.merge_documents(doc_2, doc_1, comment="comment")
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 0

    def test_merge_3(self, moderator):
        self.login_user(moderator)
        doc_1 = self.create_document(data={"type": ""}).json["document"]
        doc_2 = self.create_document(data={"type": "x"}).json["document"]
        self.merge_documents(doc_1, doc_2, comment="comment")
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_2["id"]

    def test_merge_4(self, moderator):
        self.login_user(moderator)
        doc_1 = self.create_document(data={"type": ""}).json["document"]
        doc_2 = self.create_document(data={"type": "x"}).json["document"]
        self.merge_documents(doc_2, doc_1, comment="comment")
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_1["id"]

    def test_merge_5(self, moderator):
        self.login_user(moderator)
        doc_1 = self.create_document(data={"type": "x"}).json["document"]
        doc_2 = self.create_document(data={"type": "x"}).json["document"]
        self.merge_documents(doc_1, doc_2, comment="comment")
        documents = self.get_documents(params={"t": "x"}).json["documents"]
        assert len(documents) == 1
        assert documents[0]["id"] == doc_2["id"]
