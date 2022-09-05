from cms.models.user import User


class BaseTest:
    def add_user(self, username="username", password="password", validate_email=True):
        user = User(username=username, email="a@b.c")
        user.set_password(password)

        if not validate_email:
            user.set_validation_token()

        user.create()

        return user

    def login_user(self, client, username="username", password="password", expected_status=200):
        r = client.post("/login", json={"username": username, "password": password})
        assert r.status_code == expected_status, f"Expecting status {expected_status}, got {r.status_code}: {r.json}"

        return r
