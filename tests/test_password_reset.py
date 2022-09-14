# ## Password reset

# 1. as an anonymous user, the UI send a `POST /reset_password` with the mail
# 2. if the mail does not exists, or is not validated, the process stops (though, a normal response is sent)
# 3. A one-usage token is generated and sent to the user via a mail as a UI link like `/login?name=xx&token=yy`
# 4. The UI is responsible to do a `POST /login` with the username/token present in the request query
# 5. User is logged, and the token is removed.
# 6. UI is reponsible to show a password reset page
from datetime import timedelta, datetime

from freezegun import freeze_time

from tests.utils import BaseTest


class Test_PasswordReset(BaseTest):
    def test_simple(self):
        user = self.db_add_user()
        r = self.post("/reset_password", json={"email": user._email})
        assert r.status_code == 200
        assert "expiration_date" in r.json

        self.login_user(expected_status=200)
        self.logout_user(expected_status=200)

        token = self.get_login_token(user.name)
        assert token is not None
        r = self.post("/login", json={"name": user.name, "token": token})
        assert r.status_code == 200, r.json

        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["email"] == user._email

        self.logout_user(expected_status=200)

        # test unique usage
        r = self.post("/login", json={"name": user.name, "token": token})
        assert r.status_code == 401

    def test_email_not_found(self):
        r = self.post("/reset_password", json={"email": "i_do@not_exists.fr"})
        assert r.status_code == 200

    def test_user_is_not_validated(self):
        user = self.db_add_user(validate_email=False)
        r = self.post("/reset_password", json={"email": user._email_to_validate})
        assert r.status_code == 200
        assert self.get_login_token(user.name) is None

    def test_bad_token(self):
        user = self.db_add_user()
        r = self.post("/reset_password", json={"email": user._email})
        assert r.status_code == 200, r.json

        r = self.post("/login", json={"name": user.name, "token": "not the token"})
        assert r.status_code == 401, r.json

    def test_several_request(self):
        user = self.db_add_user()

        r = self.post("/reset_password", json={"email": user._email})
        assert r.status_code == 200
        token_1 = self.get_login_token(user.name)

        r = self.post("/reset_password", json={"email": user._email})
        assert r.status_code == 200
        token_2 = self.get_login_token(user.name)

        assert token_1 is not None
        assert token_2 is not None
        assert token_1 != token_2

        r = self.post("/login", json={"name": user.name, "token": token_1})
        assert r.status_code == 401

        r = self.post("/login", json={"name": user.name, "token": token_2})
        assert r.status_code == 200

    def test_expiration(self):
        user = self.db_add_user()

        r = self.post("/reset_password", json={"email": user._email})
        token = self.get_login_token(user.name)

        with freeze_time(datetime.now() + timedelta(days=3)):
            r = self.post("/login", json={"name": user.name, "token": token})
            assert r.status_code == 401
