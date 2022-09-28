from tests.unit_tests.utils import BaseTest


def _assert_conflict_reponse(r):
    result = r.json
    assert "data" in result
    assert "last_version" in result["data"]
    assert "your_version" in result["data"]

    if result["data"]["last_version"] is not None:
        assert result["data"]["your_version"]["version_id"] != result["data"]["last_version"]["version_id"]


class Test_Conflict(BaseTest):
    def test_basic(self, admin):
        self.login_user(admin)

        v0 = self.create_document().json["document"]
        v1 = self.modify_document(v0).json["document"]
        r = self.modify_document(v0, expected_status=409)
        _assert_conflict_reponse(r)

        v2 = self.modify_document(v1).json["document"]
        r = self.modify_document(v0, expected_status=409)
        _assert_conflict_reponse(r)
        r = self.modify_document(v1, expected_status=409)
        _assert_conflict_reponse(r)

        self.delete_version(v1)
        # v1 is availabble in DB. Though, it should raise an error as v2 exists
        r = self.modify_document(v0, expected_status=409)
        _assert_conflict_reponse(r)

        self.delete_version(v2)
        # now, v0 is the last version, so I can modify from it
        self.modify_document(v0, expected_status=200)
