from cms import database
from cms.models.user import User


class BaseTest:
    client = None

    def _assert_status_response(self, r):
        assert r.json is not None, r
        assert "status" in r.json, r.json

        if r.status_code == 200:
            assert r.json["status"] == "ok", r.json
        else:
            assert r.json["status"] == "error", r.json
            assert "description" in r.json, r.json

    def get(self, *args, **kwargs):
        r = BaseTest.client.get(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def post(self, *args, **kwargs):
        r = BaseTest.client.post(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def put(self, *args, **kwargs):
        r = BaseTest.client.put(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def delete(self, *args, **kwargs):
        r = BaseTest.client.delete(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def db_add_user(
        self, name="name", email=None, password="password", validate_email=True, roles="", perform_login=False
    ):
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

    def login_user(self, user="name", password="password", expected_status=200):

        name = user if isinstance(user, str) else user.name

        r = self.post("/login", json={"name": name, "password": password})
        assert r.status_code == expected_status, f"Expecting status {expected_status}, got {r.status_code}: {r.json}"

        return r

    def logout_user(self, expected_status=200):
        r = self.delete("/login")
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

    # helpers
    def create_document(self, namespace="x", data=None, expected_status=200):
        r = self.put("/documents", json={"document": {"namespace": namespace, "data": data if data else {}}})

        assert r.status_code == expected_status, r.json

        return r

    def modify_document(self, document, data=None, expected_status=200):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.post(f"/document/{document_id}", json={"document": {"namespace": "", "data": data if data else {}}})

        assert r.status_code == expected_status, r.json

        return r

    def hide_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.put(f"/hide_version/{version_id}", json={"comment": "some comment"})
        assert r.status_code == expected_status

        return r

    def unhide_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.delete(f"/hide_version/{version_id}", json={"comment": "some comment"})
        assert r.status_code == expected_status

        return r

    def protect_document(self, document_id, expected_status=200):
        r = self.put(f"/protect_document/{document_id}", json={"comment": "some comment"})
        assert r.status_code == expected_status

        return r

    def unprotect_document(self, document_id, expected_status=200):
        r = self.delete(f"/protect_document/{document_id}", json={"comment": "some comment"})
        assert r.status_code == expected_status

        return r

    def block_user(self, user, expected_status=200):
        r = self.put(f"/block_user/{user.id}", json={"comment": "Some comment"})
        assert r.status_code == expected_status, r.json
        return r

    def unblock_user(self, user, expected_status=200):
        r = self.delete(f"/block_user/{user.id}", json={"comment": "Some comment"})
        assert r.status_code == expected_status, r.json
        return r
