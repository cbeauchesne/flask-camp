from tests.unit_tests.utils import BaseTest


class Test_ETag(BaseTest):
    def test_main(self, user):
        self.login_user(user)

        v1 = self.create_document(data={"value": "42"}).json["document"]
        r = self.get_document(v1)
        assert "ETag" in r.headers, r.headers
        assert self.api.memory_cache.get_document(v1["id"])["timestamp"] == v1["timestamp"]
        etag = r.headers["ETag"]

        self.get_document(v1, headers={"If-None-Match": etag}, expected_status=304)
        self.get_document(v1, headers={"If-None-Match": "not-the-good-hash"}, expected_status=200)

        # a modification remove the document from the cache
        v2 = self.modify_document(v1, data="12").json["document"]
        assert self.api.memory_cache.get_document(v1["id"]) is None

        # but a get recompute it in the cache
        self.get_document(v1)
        assert self.api.memory_cache.get_document(v1["id"]) is not None
        assert self.api.memory_cache.get_document(v1["id"])["timestamp"] == v2["timestamp"]

        r = self.get_document(v1, headers={"If-None-Match": etag}, expected_status=200)

    def test_memcache_failure(self, user):
        self.login_user(user)

        doc = self.create_document().json["document"]
        self.api.memory_cache.delete_document(doc["id"])
        self.get_document(doc, expected_status=200)
