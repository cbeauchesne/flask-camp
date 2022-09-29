import pytest

from tests.unit_tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_error(self, app):
        with pytest.raises(TypeError):
            app.cooker({})

    def test_creation(self, user, app, memory_cache):
        self.login_user(user)

        @app.cooker
        def cooker(document):
            document["cooked"] = True

        doc = self.create_document(namespace="x", data={"value": "42"}).json["document"]
        assert doc["cooked"] is True

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
