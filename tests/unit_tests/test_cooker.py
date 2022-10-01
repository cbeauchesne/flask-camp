import pytest

from tests.unit_tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_error(self, app):
        with pytest.raises(TypeError):
            app.cooker({})

    def test_basic(self, user, app, memory_cache):
        self.login_user(user)

        @app.cooker
        def cooker(document, get_document):  # pylint: disable=unused-argument
            document["cooked"] = True

        doc = self.create_document(namespace="x", data={"value": "42"}).json["document"]
        assert doc["cooked"] is True, doc

        doc = self.get_document(doc).json["document"]
        assert doc["cooked"] is True

        doc = self.modify_document(doc).json["document"]
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

        assert "cooked" not in memory_cache.get_document(doc["id"])
        assert "cooked" in memory_cache.get_cooked_document(doc["id"])

    def test_association(self, app, moderator, admin):
        @app.cooker
        def cooker(document, get_document):
            # Let's build an app with document. One rule: all documents have (or not) a parent
            # if a document has a parent, it must be present in document["parent"]
            parent_id = document["data"]["parent_id"]
            if parent_id is not None:
                document["parent"] = get_document(parent_id)
            else:
                document["parent"] = None

        self.login_user(moderator)

        # create a doc
        parent_v1 = self.create_document(data={"parent_id": None, "content": "v1"}).json["document"]

        # create another doc. It's parent is doc_1
        child = self.create_document(data={"parent_id": parent_v1["id"]}).json["document"]
        assert "parent" in child
        assert child["parent"]["id"] == parent_v1["id"]
        assert child["parent"]["data"]["content"] == "v1"

        # now, modify the parent
        parent_v2 = self.modify_document(parent_v1, data={"parent_id": None, "content": "v2"}).json["document"]

        # the child must have the updated value of the parent
        child = self.get_document(child).json["document"]

        # not let's try to hide a version, the child must have the first value of the parent
        self.hide_version(parent_v2)
        child = self.get_document(child).json["document"]
        assert child["parent"]["data"]["content"] == "v1"
        assert child["parent"]["version_id"] == parent_v1["version_id"]

        # unhide it, back to parent v2
        self.unhide_version(parent_v2)
        child = self.get_document(child).json["document"]
        assert child["parent"]["data"]["content"] == "v2"
        assert child["parent"]["version_id"] == parent_v2["version_id"]

        # delete parent v2, again v1 should appear
        self.login_user(admin)
        self.delete_version(parent_v2)
        child = self.get_document(child).json["document"]
        assert child["parent"]["data"]["content"] == "v1"
        assert child["parent"]["version_id"] == parent_v1["version_id"]

        # Now, delete the parent
        self.delete_document(parent_v1)
        child = self.get_document(child).json["document"]
        assert child["parent"] is None

    def test_circular_reference(self, app, user):
        @app.cooker
        def cooker(document, get_document):
            # Let's build an app with document. One rule: all documents have (or not) a parent
            # if a document has a parent, it must be present in document["parent"]
            parent_id = document["data"]["parent_id"]
            if parent_id is not None:
                document["parent"] = get_document(parent_id)
            else:
                document["parent"] = None

        self.login_user(user)
        twin_a = self.create_document(data={"parent_id": None}).json["document"]
        twin_b = self.create_document(data={"parent_id": twin_a["id"]}).json["document"]

        twin_a = self.modify_document(twin_a, data={"parent_id": twin_b["id"]}).json["document"]
        assert twin_a["parent"]["version_id"] == twin_b["version_id"]

        twin_a = self.get_document(twin_a).json["document"]
        assert twin_a["parent"]["version_id"] == twin_b["version_id"]

        twin_b = self.get_document(twin_b).json["document"]
        assert twin_b["parent"]["version_id"] == twin_a["version_id"]

        # self reference
        narcissus = self.create_document(data={"parent_id": None}).json["document"]
        narcissus = self.modify_document(narcissus, data={"parent_id": narcissus["id"]}).json["document"]
        assert "parent" in narcissus, narcissus
        assert narcissus["parent"]["version_id"] == narcissus["version_id"]
