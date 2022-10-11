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
    def reset_password_and_get_token(self, user):
        with self.api.mail.record_messages() as outbox:
            r = self.reset_password(user._email)
            assert "expiration_date" in r.json
            token = re.sub(r"^(.*login_token=)", "", outbox[0].body)

        return token

    def test_simple(self, user):
        token = self.reset_password_and_get_token(user)

        self.login_user(user, expected_status=200)
        self.logout_user(expected_status=200)

        self.login_user(user, token=token, expected_status=200)

        r = self.get_user(user)
        assert r.json["user"]["email"] == user._email

        self.modify_user(user, token=token, new_password="a_new_pass")

        self.logout_user(expected_status=200)

        # test unique usage
        self.login_user(user, token=token, expected_status=401)

        # test that password has been updated
        self.login_user(user, password="password", expected_status=401)
        self.login_user(user, password="a_new_pass", expected_status=200)

    def test_email_not_found(self):
        with self.api.mail.record_messages() as outbox:
            self.reset_password("i_do@not_exists.fr", expected_status=200)
            assert len(outbox) == 0

    def test_user_is_not_validated(self, unvalidated_user):
        with self.api.mail.record_messages() as outbox:
            self.reset_password(unvalidated_user._email_to_validate, expected_status=200)
            assert len(outbox) == 0

    def test_bad_token(self, user):
        self.reset_password(user._email, expected_status=200)
        self.login_user(user, token="not the token", expected_status=401)

    def test_several_request(self, user):
        token_1 = self.reset_password_and_get_token(user)
        token_2 = self.reset_password_and_get_token(user)

        assert token_1 is not None
        assert token_2 is not None
        assert token_1 != token_2

        self.login_user(user, token=token_1, expected_status=401)
        self.login_user(user, token=token_2, expected_status=200)

    def test_expiration(self, user):

        token = self.reset_password_and_get_token(user)

        with freeze_time(datetime.now() + timedelta(days=3)):
            self.login_user(user, token=token, expected_status=401)
