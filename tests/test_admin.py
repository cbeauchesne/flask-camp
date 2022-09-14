from tests.utils import BaseTest


class Test_Admin(BaseTest):
    def test_right_attribution(self):
        admin = self.db_add_user(roles="admin")
        user = self.db_add_user("basic_user")

        self.login_user(user.name)

        r = self.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json

        r = self.get(f"/user/{user.id}")
        assert r.status_code == 200, r.json
        assert r.json["user"]["roles"] == []

        self.logout_user()

        self.login_user(admin.name)
        r = self.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json
        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["roles"] == ["moderator"]
