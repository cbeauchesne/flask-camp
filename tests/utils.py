from cms.models.user import User


class BaseTest:
    def add_user(self, username="username", password="password"):
        user = User(username=username, email="a@b.c")
        user.set_password(password)
        user.create()

        return user

    def login_user(self, client, username="username", password="password"):
        r = client.post("/login", json={"username": username, "password": password})
        assert r.status_code == 200, r
