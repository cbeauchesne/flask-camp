import pytest

from flask_camp import RestApi
from flask_camp.exceptions import ConfigurationError

from tests.unit_tests.utils import BaseTest


def cooker(document, get_document):
    data = document.get("data")

    if isinstance(data, dict) and data.get("namespace") in ("cook-me",):
        document["cooked"] = {}

        # Let's build an app with document. One rule: all documents have (or not) a parent
        # if a document has a parent, it must be present in document["cooked"]["parent"]
        parent_id = document["data"].get("parent_id")
        if parent_id is not None:
            document["cooked"]["parent"] = get_document(parent_id)
        else:
            document["cooked"]["parent"] = None


class Test_Cooker(BaseTest):
    rest_api_kwargs = {"cooker": cooker}

    def test_error(self):
        with pytest.raises(ConfigurationError):
            RestApi(cooker={})

    def test_basic(self, user):
        self.login_user(user)

        doc = self.create_document(data={"namespace": "cook-me", "value": "42"}).json["document"]
        assert "cooked" in doc, doc

        doc = self.get_document(doc).json["document"]
        assert "cooked" in doc

        doc = self.modify_document(doc).json["document"]
        assert "cooked" in doc

        doc = self.get_version(doc).json["document"]
        assert "cooked" in doc

        docs = self.get_documents().json["documents"]
        assert "cooked" in docs[0]

        docs = self.get_versions().json["versions"]
        assert "cooked" in docs[0]

        self.add_user_tag("star", doc)
        docs = self.get_documents(tag_name="star").json["documents"]
        assert "cooked" in docs[0]

        assert "cooked" not in self.api.memory_cache.get_document(doc["id"])
        assert "cooked" in self.api.memory_cache.get_cooked_document(doc["id"])

    def test_association(self, moderator, admin):
        # Reminder: the tested app havea cooker: documents have (or not) a parent
        # if a document has a parent, it must be present in document["parent"]

        self.login_user(moderator)

        # create a doc
        parent_v1 = self.create_document(
            data={"namespace": "cook-me", "parent_id": None, "content": "v1"},
        ).json["document"]

        # create another doc. It's parent is doc_1
        child = self.create_document(data={"namespace": "cook-me", "parent_id": parent_v1["id"]}).json["document"]
        assert "cooked" in child
        assert "parent" in child["cooked"]
        assert child["cooked"]["parent"]["id"] == parent_v1["id"]
        assert child["cooked"]["parent"]["data"]["content"] == "v1"

        # now, modify the parent
        parent_v2 = self.modify_document(
            parent_v1, data={"namespace": "cook-me", "parent_id": None, "content": "v2"}
        ).json["document"]

        # the child must have the updated value of the parent
        child = self.get_document(child).json["document"]

        # not let's try to hide a version, the child must have the first value of the parent
        self.hide_version(parent_v2)
        child = self.get_document(child).json["document"]
        assert child["cooked"]["parent"]["data"]["content"] == "v1"
        assert child["cooked"]["parent"]["version_id"] == parent_v1["version_id"]

        # unhide it, back to parent v2
        self.unhide_version(parent_v2)
        child = self.get_document(child).json["document"]
        assert child["cooked"]["parent"]["data"]["content"] == "v2"
        assert child["cooked"]["parent"]["version_id"] == parent_v2["version_id"]

        # delete parent v2, again v1 should appear
        self.login_user(admin)
        self.delete_version(parent_v2)
        child = self.get_document(child).json["document"]
        assert child["cooked"]["parent"]["data"]["content"] == "v1"
        assert child["cooked"]["parent"]["version_id"] == parent_v1["version_id"]

        # Now, delete the parent
        self.delete_document(parent_v1)
        child = self.get_document(child).json["document"]
        assert child["cooked"]["parent"] is None

    def test_circular_reference(self, user):

        self.login_user(user)
        twin_a = self.create_document(data={"namespace": "cook-me", "parent_id": None}).json["document"]
        twin_b = self.create_document(data={"namespace": "cook-me", "parent_id": twin_a["id"]}).json["document"]

        twin_a = self.modify_document(twin_a, data={"namespace": "cook-me", "parent_id": twin_b["id"]}).json["document"]
        assert twin_a["cooked"]["parent"]["version_id"] == twin_b["version_id"]

        twin_a = self.get_document(twin_a).json["document"]
        assert twin_a["cooked"]["parent"]["version_id"] == twin_b["version_id"]

        twin_b = self.get_document(twin_b).json["document"]
        assert twin_b["cooked"]["parent"]["version_id"] == twin_a["version_id"]

        # self reference
        narcissus = self.create_document(data={"namespace": "cook-me", "parent_id": None}).json["document"]
        narcissus = self.modify_document(narcissus, data={"namespace": "cook-me", "parent_id": narcissus["id"]}).json[
            "document"
        ]

        assert "cooked" in narcissus, narcissus
        assert "parent" in narcissus["cooked"], narcissus["cooked"]
        assert narcissus["cooked"]["parent"]["version_id"] == narcissus["version_id"]
