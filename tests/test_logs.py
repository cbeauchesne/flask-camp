from tests.utils import BaseTest


class Test_Logs(BaseTest):
    def test_anonymous_get(self):
        r = self.get("/logs")
        assert r.status_code == 200

    def test_hide_version(self):
        moderator = self.add_user(roles="moderator")
        self.login_user()

        doc = self.put_document().json["document"]
        self.post_document(doc["id"], data="v2")

        self.hide_version(doc)
        self.unhide_version(doc)

        r = self.get("/logs")

        assert r.status_code == 200
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
        r = self.get("/logs", query_string={"limit": 101})
        assert r.status_code == 400

    def test_typical_scenario(self):
        moderator = self.add_user(roles="moderator")
        user = self.add_user("user")

        self.login_user()
        self.block_user(user)
        self.unblock_user(user)

        doc = self.put_document().json["document"]

        self.protect_document(document_id=doc["id"])
        self.unprotect_document(document_id=doc["id"])

        self.logout_user()
        admin = self.add_user(name="admin", roles="admin")
        self.login_user("admin")

        self.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        self.post(f"/user/{user.id}", json={"roles": ["admin"]})
        self.post(f"/user/{user.id}", json={"roles": ["admin", "robot"]})
        self.post(f"/user/{user.id}", json={"roles": []})

        r = self.get("/logs")

        assert r.status_code == 200
        assert r.json["count"] == 10, r.json

        logs = r.json["logs"]

        assert logs[-1]["action"] == "block"
        assert logs[-1]["target_user"]["id"] == user.id
        assert logs[-1]["user"]["id"] == moderator.id
        assert logs[-2]["action"] == "unblock"
        assert logs[-2]["target_user"]["id"] == user.id
        assert logs[-2]["user"]["id"] == moderator.id

        assert logs[-3]["action"] == "protect"
        assert logs[-3]["document_id"] == doc["id"]
        assert logs[-3]["user"]["id"] == moderator.id
        assert logs[-4]["action"] == "unprotect"
        assert logs[-4]["document_id"] == doc["id"]
        assert logs[-4]["user"]["id"] == moderator.id

        assert logs[-5]["action"] == "add_role moderator"
        assert logs[-5]["target_user"]["id"] == user.id
        assert logs[-5]["user"]["id"] == admin.id

        assert logs[-6]["action"] == "remove_role moderator"
        assert logs[-6]["target_user"]["id"] == user.id
        assert logs[-6]["user"]["id"] == admin.id

        assert logs[-7]["action"] == "add_role admin"
        assert logs[-7]["target_user"]["id"] == user.id
        assert logs[-7]["user"]["id"] == admin.id

        assert logs[-8]["action"] == "add_role robot"
        assert logs[-8]["target_user"]["id"] == user.id
        assert logs[-8]["user"]["id"] == admin.id

        assert logs[-9]["action"] == "remove_role admin"
        assert logs[-9]["target_user"]["id"] == user.id
        assert logs[-9]["user"]["id"] == admin.id

        assert logs[-10]["action"] == "remove_role robot"
        assert logs[-10]["target_user"]["id"] == user.id
        assert logs[-10]["user"]["id"] == admin.id
