import pytest

from tests.unit_tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_error(self, app):
        with pytest.raises(TypeError):
            app.cooker({})

    def test_basic(self, user, app, memory_cache):
        self.login_user(user)

        @app.cooker
        def cooker(document):
            document["cooked"] = True
            return []

        doc = self.create_document(namespace="x", data={"value": "42"}).json["document"]
        assert doc["cooked"] is True, doc

        doc = self.get_document(doc).json["document"]
        assert doc["cooked"] is True

        doc = self.get_version(doc).json["document"]
        assert doc["cooked"] is True

        docs = self.get_documents().json["documents"]
        assert docs[0]["cooked"] is True

        docs = self.get_versions().json["versions"]
        assert docs[0]["cooked"] is True

        self.add_user_tag("star", doc)
        docs = self.get_tagged_documents("star").json["documents"]
        assert docs[0]["cooked"] is True

        assert "cooked" not in memory_cache._document.get(doc["id"])
        assert "cooked" in memory_cache._cooked_document.get(doc["id"])

    def test_association(self, user, app):
        self.login_user(user)

        @app.cooker
        def cooker(document):
            # Let's build an app with document. One rule: all document have (or not) a parent
            # if a document have a parent, it must be present in document["parent"]
            parent_id = document["data"]["parent_id"]
            if parent_id is not None:
                document["parent"] = app.get_document(parent_id)
            else:
                document["parent"] = None

            return [parent_id]  # return the list of dodument id used by the cooker

        # create a doc
        doc_1 = self.create_document(data={"parent_id": None, "content": "v1"}).json["document"]

        # create another doc. It's parent is doc_1
        doc_2 = self.create_document(data={"parent_id": doc_1["id"]}).json["document"]
        assert "parent" in doc_2
        assert doc_2["parent"]["id"] == doc_1["id"]
        assert doc_2["parent"]["data"]["content"] == "v1"

        # now, modify the parent
        self.modify_document(doc_1, data={"parent_id": None, "content": "v2"})

        # the child must have the updated value of the parent
        doc_2 = self.get_document(doc_2).json["document"]
        assert doc_2["parent"]["data"]["content"] == "v2"

        # TODO : test: a depends of b and b depends of a
