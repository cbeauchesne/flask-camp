from tests.utils import BaseTest


class Test_Admin(BaseTest):
    def test_right_attribution(self, client):
        admin = self.add_user(roles="admin")
        user = self.add_user("basic_user")

        self.login_user(client, user.username)

        r = client.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json

        r = client.get(f"/user/{user.id}")
        assert r.json["user"]["roles"] == []

        self.logout_user(client)

        self.login_user(client, admin.username)
        r = client.post(f"/user/{user.id}", json={"roles": ["moderator"]})
        assert r.status_code == 200, r.json
        r = client.get(f"/user/{user.id}")
        assert r.json["user"]["roles"] == ["moderator"]
