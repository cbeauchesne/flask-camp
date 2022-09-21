# ## Password reset

# 1. as an anonymous user, the UI send a `POST /reset_password` with the mail
# 2. if the mail does not exists, or is not validated, the process stops (though, a normal response is sent)
# 3. A one-usage token is generated and sent to the user via a mail as a UI link like `/login?name=xx&token=yy`
# 4. The UI is responsible to do a `POST /login` with the username/token present in the request query
# 5. User is logged, and the token is removed.
# 6. UI is reponsible to show a password reset page
from datetime import timedelta, datetime
import re

from freezegun import freeze_time

from tests.unit_tests.utils import BaseTest


class Test_PasswordReset(BaseTest):
    def reset_password(self, mail, user):
        with mail.record_messages() as outbox:
            r = self.post("/reset_password", json={"email": user._email})
            assert r.status_code == 200
            assert "expiration_date" in r.json
            token = re.sub(r"^(.*login_token=)", "", outbox[0].body)

        return token

    def test_simple(self, user, mail):
        token = self.reset_password(mail, user)

        self.login_user(user, expected_status=200)
        self.logout_user(expected_status=200)

        r = self.post("/login", json={"name": user.name, "token": token})
        assert r.status_code == 200, r.json

        r = self.get(f"/user/{user.id}")
        assert r.json["user"]["email"] == user._email

        self.logout_user(expected_status=200)

        # test unique usage
        r = self.post("/login", json={"name": user.name, "token": token})
        assert r.status_code == 401

    def test_email_not_found(self, mail):
        with mail.record_messages() as outbox:
            r = self.post("/reset_password", json={"email": "i_do@not_exists.fr"})
            assert len(outbox) == 0

        assert r.status_code == 200

    def test_user_is_not_validated(self, unvalidated_user, mail):
        with mail.record_messages() as outbox:
            r = self.post("/reset_password", json={"email": unvalidated_user._email_to_validate})
            assert len(outbox) == 0
            assert r.status_code == 200

    def test_bad_token(self, user):
        r = self.post("/reset_password", json={"email": user._email})
        assert r.status_code == 200, r.json

        r = self.post("/login", json={"name": user.name, "token": "not the token"})
        assert r.status_code == 401, r.json

    def test_several_request(self, mail, user):
        token_1 = self.reset_password(mail, user)
        token_2 = self.reset_password(mail, user)

        assert token_1 is not None
        assert token_2 is not None
        assert token_1 != token_2

        r = self.post("/login", json={"name": user.name, "token": token_1})
        assert r.status_code == 401

        r = self.post("/login", json={"name": user.name, "token": token_2})
        assert r.status_code == 200

    def test_expiration(self, user, mail):

        token = self.reset_password(mail, user)

        with freeze_time(datetime.now() + timedelta(days=3)):
            r = self.post("/login", json={"name": user.name, "token": token})
            assert r.status_code == 401
