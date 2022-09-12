from cms import database
from cms.application import Application
from cms.models.user import User


class BaseTest:
    app = None
    client = None

    def setup_method(self, test_method):  # pylint: disable=unused-argument
        self.app = Application(TESTING=True)
        self.app.create_all()
        self.client = self.app.test_client()
        self.client.__enter__()  # pylint: disable=unnecessary-dunder-call

    def teardown_method(self, test_method):  # pylint: disable=unused-argument
        self.client.__exit__(None, None, None)

    def _assert_status_response(self, r):
        if r.status_code == 200:
            assert r.json["status"] == "ok", r.json
        else:
            assert "message" in r.json, r.json

    def get(self, *args, **kwargs):
        r = self.client.get(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def post(self, *args, **kwargs):
        r = self.client.post(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def put(self, *args, **kwargs):
        r = self.client.put(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def delete(self, *args, **kwargs):
        r = self.client.delete(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def add_user(self, name="name", email=None, password="password", validate_email=True, roles=""):
        user = User(
            name=name,
            roles=roles
            if isinstance(roles, (list, tuple))
            else [
                roles,
            ],
        )
        user.set_password(password)

        user.set_email(email if email else f"{name}@site.org")

        if validate_email:
            user.validate_email(user._email_token)

        user.create()

        return User(
            id=user.id,
            name=user.name,
            _email=user._email,
            _email_to_validate=user._email_to_validate,
            _email_token=user._email_token,
            roles=user.roles,
        )

    def login_user(self, name="name", password="password", expected_status=200):
        r = self.post("/login", json={"name": name, "password": password})
        assert r.status_code == expected_status, f"Expecting status {expected_status}, got {r.status_code}: {r.json}"

        return r

    def logout_user(self, expected_status=200):
        r = self.get("/logout")
        assert r.status_code == expected_status, r.json
        return r

    def get_email_token(self, name):
        users = database.execute(f"SELECT id, email_token FROM user WHERE name='{name}'")
        user = list(users)[0]

        return user["email_token"]

    def get_login_token(self, name):
        users = database.execute(f"SELECT id, login_token FROM user WHERE name='{name}'")
        user = list(users)[0]

        return user["login_token"]

    def put_document(self, namespace="x", data=None):
        return self.put("/documents", json={"document": {"namespace": namespace, "data": data if data else {}}})

    def post_document(self, id, data=None):
        return self.post(f"/document/{id}", json={"document": {"namespace": "", "data": data if data else {}}})
