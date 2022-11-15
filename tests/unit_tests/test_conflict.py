import pytest
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

        # modify from v0, where v1 exists => error
        r = self.modify_document(v0, expected_status=409)
        _assert_conflict_reponse(r)

        # modify from v1, where v1 is the last version => ok
        self.modify_document(v1)

        # modify from v0, where v2 is the last version => error
        r = self.modify_document(v0, expected_status=409)
        _assert_conflict_reponse(r)

        # modify from v1, where v2 is the last version => error
        r = self.modify_document(v1, expected_status=409)
        _assert_conflict_reponse(r)

        # modify from v1, where v1 does not exists, and v2 exists => error
        self.delete_version(v1)
        r = self.modify_document(v1, expected_status=409)
        _assert_conflict_reponse(r)

        # modify from v0, where v1 does not exists, and v2 exists => error
        r = self.modify_document(v0, expected_status=409)
        _assert_conflict_reponse(r)

    @pytest.mark.xfail(reason="Not possible yest to delete last version")
    def test_delete_vast_version(self, admin):
        self.login_user(admin)

        v0 = self.create_document().json["document"]
        v1 = self.modify_document(v0).json["document"]

        # modify from v0, where v1 exists => error
        r = self.modify_document(v0, expected_status=409)
        _assert_conflict_reponse(r)

        self.delete_version(v1)
        # now, v0 is the last version, so I can modify from it
        self.modify_document(v0, expected_status=200)
