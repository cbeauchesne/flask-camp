from cms import database
from cms.application import Application
from cms.models.user import User


class BaseTest:
    def setup_method(self, test_method):
        self.app = Application(TESTING=True)
        self.app.create_all()
        self.client = self.app.test_client()
        self.client.__enter__()

    def teardown_method(self, test_method):
        self.client.__exit__(None, None, None)

    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.client.delete(*args, **kwargs)

    def add_user(self, name="name", email=None, password="password", validate_email=True, roles=""):
        user = User(name=name, roles=roles)
        user.set_password(password)

        email = email if email else f"{name}@site.org"

        if not validate_email:
            user.email_to_validate = email
            user.set_validation_token()
        else:
            user.email = email

        user.create()

        return User(
            id=user.id,
            name=user.name,
            email=user.email,
            email_to_validate=user.email_to_validate,
            validation_token=user.validation_token,
            roles=user.roles,
        )

    def login_user(self, name="name", password="password", expected_status=200):
        r = self.post("/login", json={"name": name, "password": password})
        assert r.status_code == expected_status, f"Expecting status {expected_status}, got {r.status_code}: {r.json}"

        return r

    def logout_user(self):
        return self.get("/logout")

    def get_validation_token(self, name):
        users = database.execute(f"SELECT id, validation_token FROM user WHERE name='{name}'")
        user = [user for user in users][0]

        token = user["validation_token"]
        user_id = user["id"]

        return user_id, token
