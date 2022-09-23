import re
import pytest
from tests.unit_tests.utils import BaseTest


class Test_UserCreation(BaseTest):
    def test_typical_scenario(self, mail):
        name, email, password = "my_user", "a@b.c", "week password"

        with mail.record_messages() as outbox:
            r = self.create_user(name, email, password, expected_status=200)
            assert len(outbox) == 1
            assert outbox[0].subject == "Welcome to example.com"
            body = outbox[0].body
            token = re.sub(r"^(.*email_token=)", "", body)

        assert r.json["status"] == "ok"

        user = r.json["user"]

        assert len(user) == 5, user
        assert "id" in user
        assert "ui_preferences" in user
        assert user["blocked"] is False
        assert user["name"] == name
        assert user["roles"] == []

        self.validate_email(user=user, token=token, expected_status=200)

        # user should not be logged
        r = self.get_user(user)
        assert "email" not in r.json["user"]  # email is a private value

        r = self.login_user(name, password, expected_status=200)

        assert len(r.json["user"]) == 6, r.json["user"]
        assert r.json["user"]["id"] == user["id"]
        assert r.json["user"]["blocked"] is False
        assert r.json["user"]["ui_preferences"] is None
        assert r.json["user"]["name"] == name
        assert r.json["user"]["email"] == email
        assert r.json["user"]["roles"] == []

        r = self.logout_user()

    def test_errors_on_token_validation(self, unvalidated_user):

        r = self.login_user(unvalidated_user, expected_status=401)
        assert r.json["description"] == "User's email is not validated"

        r = self.post("/validate_email", json={"name": unvalidated_user.name}, expected_status=400)
        assert r.json["description"] == "'token' is a required property on instance "

        self.post(
            "/validate_email",
            json={"name": "not_the_name", "token": unvalidated_user._email_token},
            expected_status=404,
        )

        r = self.validate_email(unvalidated_user, token="not the good one", expected_status=401)
        assert r.json["description"] == "Token doesn't match"

        r = self.login_user(unvalidated_user, expected_status=401)
        assert r.json["description"] == "User's email is not validated"

        self.validate_email(unvalidated_user, token=unvalidated_user._email_token, expected_status=200)

        r = self.validate_email(unvalidated_user, token=unvalidated_user._email_token, expected_status=400)
        assert r.json["description"] == "There is no email to validate"

        r = self.login_user(unvalidated_user, expected_status=200)

    def test_login_errors(self, user):
        r = self.login_user("not_the_name", expected_status=401)
        assert r.json["description"] == "User [not_the_name] does not exists, or password is wrong"

        r = self.login_user(user, "not the password", expected_status=401)
        assert r.json["description"] == f"User [{user.name}] does not exists, or password is wrong"

        self.post("/login", json={"name": user.name}, expected_status=400)

    def test_logout_errors(self):
        self.delete("/login", expected_status=403)

    def test_notfound_errors(self, user):
        self.login_user(user)
        self.get("/user/42", expected_status=404)

    def test_anonymous_get(self, user):
        self.get_user(user, expected_status=200)

    def test_name_errors(self):
        email, password = "valid@email.com", "password"

        self.create_user("", email, password, expected_status=400)
        self.create_user(" starting_space", email, password, expected_status=400)
        self.create_user("abc", email, password, expected_status=400)  # too short
        self.create_user("@xxxx", email, password, expected_status=400)  # can't contains an @
        self.create_user("aaa@aaa", email, password, expected_status=400)  # same
        self.create_user("x" * 1000, email, password, expected_status=400)  # too long

    def test_email_error(self):
        name, password = "valid_name", "password"

        self.put("/users", json={"name": name, "email": None, "password": password}, expected_status=400)
        self.create_user(name, "", password, 400)
        self.create_user(name, "a.fr", password, 400)

    def test_create_while_logged(self, user):
        self.login_user(user)
        self.create_user("other", "a@b.c", "p", 400)

    def test_admin_can_resend_email(self, admin, mail):
        user = self.create_user().json["user"]

        self.login_user(admin)

        with mail.record_messages() as outbox:
            self.resend_email_validation(user)
            assert len(outbox) == 1
            assert outbox[0].subject == "Welcome to example.com"
            body = outbox[0].body
            token = re.sub(r"^(.*email_token=)", "", body)

        self.logout_user()
        self.validate_email(user, token)

        self.login_user(user)

    def test_resend_validation_mail_errors(self, admin, moderator, user):
        new_user = self.create_user().json["user"]

        self.resend_email_validation(new_user, expected_status=403)

        self.login_user(user)
        self.resend_email_validation(new_user, expected_status=403)

        self.login_user(moderator)
        self.resend_email_validation(new_user, expected_status=403)

        self.login_user(admin)
        self.resend_email_validation(new_user, expected_status=200)

        self.get("/validate_email", params={"name": "not_the_name"}, expected_status=404)
        self.get("/validate_email", expected_status=400)

    @pytest.mark.usefixtures("cant_send_mail")
    def test_mail_error(self, mail):
        with mail.record_messages() as outbox:
            self.create_user(expected_status=200)
            assert len(outbox) == 0


class Test_UserModification(BaseTest):
    def test_change_password(self, user):
        self.login_user(user)

        self.modify_user(user, password="p2")

        self.logout_user()
        self.login_user(user, "p1", expected_status=401)
        self.login_user(user, "p2", expected_status=200)

    def test_change_email(self, mail, user):
        self.login_user(user)

        with mail.record_messages() as outbox:
            r = self.modify_user(user, email="other@email.com")
            assert len(outbox) == 1
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        self.logout_user()

        r = self.login_user(user)
        assert r.json["user"]["email"] == user.email  # not yet validated

        self.validate_email(user, token, expected_status=200)

        r = self.get_user(user, expected_status=200)
        assert r.json["user"]["email"] == "other@email.com", r.json

    def test_errors(self, user, user_2):
        self.login_user(user)

        r = self.modify_user(user_2, password="p2", expected_status=403)
        assert r.json["description"] == "You can't modify this user"

    def test_email_error(self, user):
        self.login_user(user)

        self.post(f"/user/{user.id}", json={"email": None, "password": "p"}, expected_status=400)
        self.modify_user(user, email="", expected_status=400)
        self.modify_user(user, email="a.fr", expected_status=400)


class Test_UserUniqueness(BaseTest):
    def test_username(self, user):
        r = self.create_user(user.name, "other@email.c", "password", expected_status=400)
        assert r.json["description"] == "A user still exists with this name"

    def test_email_at_creation(self, user):
        r = self.create_user("other_name", user._email, "password", expected_status=400)
        assert r.json["description"] == "A user still exists with this email"

    def test_email_at_modification(self, user, user_2):
        self.login_user(user)
        r = self.modify_user(user, email=user_2._email, expected_status=400)
        assert r.json["description"] == "A user still exists with this email"
        self.modify_user(user, email="mail@competition.fr", expected_status=200)
        self.logout_user()

        self.login_user(user_2)
        self.modify_user(user_2, email="mail@competition.fr", expected_status=200)
        self.logout_user()

    def test_do_not_validate_same_email(self, mail):
        with mail.record_messages() as outbox:
            user_1 = self.create_user("user1", "a@b.c", "p").json["user"]
            token_1 = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        with mail.record_messages() as outbox:
            user_2 = self.create_user("user2", "a@b.c", "p").json["user"]
            token_2 = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        self.validate_email(user=user_1, token=token_1)
        r = self.validate_email(user=user_2, token=token_2, expected_status=400)
        assert r.json["description"] == "A user still exists with this email"


class Test_Logout(BaseTest):
    def test_main(self, user):
        self.logout_user(403)
        self.login_user(user)
        self.logout_user()
        self.logout_user(403)
