from tests.unit_tests.utils import BaseTest


class Test_ETag(BaseTest):
    def test_main(self, user, memory_cache):
        self.login_user(user)

        doc = self.create_document(data={"value": "42"}).json["document"]
        r = self.get_document(doc)
        assert "ETag" in r.headers, r.headers
        etag = r.headers["ETag"]

        self.get_document(doc, headers={"If-None-Match": etag}, expected_status=304)
        self.get_document(doc, headers={"If-None-Match": "not-the-good-hash"}, expected_status=200)

        self.modify_document(doc, "12")
        r = self.get_document(doc, headers={"If-None-Match": etag}, expected_status=200)

        assert memory_cache.document.get(doc["id"]) is not None
