from tests.utils import BaseTest


class Test_Admin(BaseTest):
    def test_right_attribution(self):
        admin = self.add_user(roles="admin")
        user = self.add_user("basic_user")

        self.login_user(user.name)

        r = self.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json

        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["roles"] == []

        self.logout_user()

        self.login_user(admin.name)
        r = self.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json
        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["roles"] == ["moderator"]
