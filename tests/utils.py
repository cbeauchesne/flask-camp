from cms import database
from cms.models.user import User


class BaseTest:
    def add_user(self, username="username", email="a@b.c", password="password", validate_email=True):
        user = User(username=username)
        user.set_password(password)

        if not validate_email:
            user.email_to_validate = email
            user.set_validation_token()
        else:
            user.email = email

        user.create()

        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            email_to_validate=user.email_to_validate,
            validation_token=user.validation_token,
        )

    def login_user(self, client, username="username", password="password", expected_status=200):
        r = client.post("/login", json={"username": username, "password": password})
        assert r.status_code == expected_status, f"Expecting status {expected_status}, got {r.status_code}: {r.json}"

        return r

    def get_validation_token(self, username):
        users = database.execute(f"SELECT id, validation_token FROM user WHERE username='{username}'")
        user = [user for user in users][0]

        token = user["validation_token"]
        user_id = user["id"]

        return user_id, token
