from tests.unit_tests.utils import BaseTest


def _assert_log(log, action, user, document_id=None, version_id=None, target_user_id=None):

    assert log["action"] == action
    assert log["user"]["id"] == user.id
    assert log["document_id"] == document_id
    assert log["version_id"] == version_id
    assert log["target_user_id"] == target_user_id


class Test_Logs(BaseTest):
    rest_api_kwargs = {"user_roles": "bot,contributor"}

    def test_anonymous_get(self):
        self.get_logs()

    def test_hide_version(self, moderator):
        self.login_user(moderator)

        doc = self.create_document().json["document"]
        self.modify_document(doc, data="v2")

        self.hide_version(doc)
        self.unhide_version(doc)

        r = self.get_logs()
        assert r.json["count"] == 2, r.json

        logs = r.json["logs"]

        assert logs[-1]["action"] == "hide_version"
        assert logs[-1]["version_id"] == doc["version_id"]
        assert logs[-1]["document_id"] == doc["id"]
        assert logs[-1]["user"]["id"] == moderator.id
        assert logs[-2]["action"] == "unhide_version"
        assert logs[-2]["version_id"] == doc["version_id"]
        assert logs[-2]["document_id"] == doc["id"]
        assert logs[-2]["user"]["id"] == moderator.id

    def test_errors(self):
        self.get_logs(limit=101, expected_status=400)

    def test_typical_scenario(self, user, moderator, admin):

        self.login_user(moderator)
        self.block_user(user)
        self.unblock_user(user)

        doc = self.create_document().json["document"]
        doc_v2 = self.modify_document(doc, data="v2").json["document"]

        self.protect_document(doc)
        self.unprotect_document(doc)

        self.logout_user()
        self.login_user(admin)

        self.add_user_role(user, "moderator", "comment")
        self.remove_user_role(user, "moderator", "comment")
        self.add_user_role(user, "admin", "comment")
        self.add_user_role(user, "bot", "comment")
        self.remove_user_role(user, "admin", "comment")
        self.remove_user_role(user, "bot", "comment")

        self.delete_version(doc_v2)
        self.delete_document(doc)

        r = self.get_logs()
        assert r.json["count"] == 12, r.json

        logs = r.json["logs"]

        _assert_log(logs[-1], "block", moderator, target_user_id=user.id)
        _assert_log(logs[-2], "unblock", moderator, target_user_id=user.id)

        _assert_log(logs[-3], "protect", moderator, document_id=doc["id"])
        _assert_log(logs[-4], "unprotect", moderator, document_id=doc["id"])

        _assert_log(logs[-5], "add_role moderator", admin, target_user_id=user.id)
        _assert_log(logs[-6], "remove_role moderator", admin, target_user_id=user.id)

        _assert_log(logs[-7], "add_role admin", admin, target_user_id=user.id)
        _assert_log(logs[-8], "add_role bot", admin, target_user_id=user.id)

        _assert_log(logs[-9], "remove_role admin", admin, target_user_id=user.id)
        _assert_log(logs[-10], "remove_role bot", admin, target_user_id=user.id)

        _assert_log(logs[-11], "delete_version", admin, document_id=doc["id"], version_id=doc_v2["version_id"])
        _assert_log(logs[-12], "delete_document", admin, document_id=doc["id"])
