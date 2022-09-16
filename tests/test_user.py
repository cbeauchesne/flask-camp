import re
from tests.utils import BaseTest


class Test_UserCreation(BaseTest):
    def test_typical_scenario(self, mail):
        name, email, password = "my_user", "a@b.c", "week password"

        with mail.record_messages() as outbox:
            r = self.put("/users", json={"name": name, "email": email, "password": password})
            assert len(outbox) == 1
            assert outbox[0].subject == "Welcome to example.com"
            body = outbox[0].body
            token = re.sub(r"^(.*email_token=)", "", body)

        assert r.status_code == 200, r.json
        assert r.json["status"] == "ok"

        user = r.json["user"]

        assert len(user) == 5, user
        assert "id" in user
        assert "ui_preferences" in user
        assert user["blocked"] is False
        assert user["name"] == name
        assert user["roles"] == []

        r = self.post("/validate_email", json={"name": name, "token": token})
        assert r.status_code == 200, r.json
        assert r.json["status"] == "ok"

        # user should not be logged
        r = self.get(f"/user/{user['id']}")
        assert r.status_code == 200
        assert "email" not in r.json["user"]  # email is a private value

        r = self.login_user(name, password)
        assert r.status_code == 200
        assert r.json["status"] == "ok"

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

        r = self.post("/validate_email", json={"name": unvalidated_user.name})
        assert r.status_code == 400
        assert r.json["description"] == "'token' is a required property on instance "

        r = self.post("/validate_email", json={"name": "not_the_name", "token": unvalidated_user._email_token})
        assert r.status_code == 404

        r = self.post("/validate_email", json={"name": unvalidated_user.name, "token": "not the good one"})
        assert r.status_code == 401
        assert r.json["description"] == "Token doesn't match"

        r = self.login_user(unvalidated_user, expected_status=401)
        assert r.json["description"] == "User's email is not validated"

        r = self.post("/validate_email", json={"name": unvalidated_user.name, "token": unvalidated_user._email_token})
        assert r.status_code == 200

        r = self.post("/validate_email", json={"name": unvalidated_user.name, "token": unvalidated_user._email_token})
        assert r.status_code == 400
        assert r.json["description"] == "There is no email to validate"

        r = self.login_user(unvalidated_user, expected_status=200)

    def test_login_errors(self, user):
        r = self.login_user("not_the_name", expected_status=401)
        assert r.json["description"] == "User [not_the_name] does not exists, or password is wrong"

        r = self.login_user(user, "not the password", expected_status=401)
        assert r.json["description"] == f"User [{user.name}] does not exists, or password is wrong"

        r = self.post("/login", json={"name": user.name})
        assert r.status_code == 400, r.json

    def test_logout_errors(self):
        r = self.delete("/login")
        assert r.status_code == 403

    def test_notfound_errors(self, user):
        self.login_user(user)
        r = self.get("/user/42")
        assert r.status_code == 404

    def test_anonymous_get(self, user):
        r = self.get(f"/user/{user.id}")
        assert r.status_code == 200

    def test_name_errors(self):
        r = self.put("/users", json={"name": "", "email": "a@b.c", "password": "p"})
        assert r.status_code == 400, r.json
        r = self.put("/users", json={"name": " dodo", "email": "a@b.c", "password": "p"})
        assert r.status_code == 400, r.json
        r = self.put("/users", json={"name": "abc", "email": "a@b.c", "password": "p"})
        assert r.status_code == 400, r.json
        r = self.put("/users", json={"name": "@xxx", "email": "a@b.c", "password": "p"})
        assert r.status_code == 400, r.json
        r = self.put("/users", json={"name": "xxx@xxx", "email": "a@b.c", "password": "p"})
        assert r.status_code == 400, r.json
        r = self.put("/users", json={"name": "x" * 1000, "email": "a@b.c", "password": "p"})
        assert r.status_code == 400, r.json

    def test_email_error(self):
        r = self.put("/users", json={"name": "xxxx", "email": None, "password": "p"})
        assert r.status_code == 400, r.json
        r = self.put("/users", json={"name": "xxxx", "email": "", "password": "p"})
        assert r.status_code == 400, r.json
        r = self.put("/users", json={"name": "xxxx", "email": "a.fr", "password": "p"})
        assert r.status_code == 400, r.json


class Test_UserModification(BaseTest):
    def test_change_password(self, user):
        self.login_user(user)

        r = self.post(f"/user/{user.id}", json={"password": "p2"})
        assert r.status_code == 200, r.json

        self.logout_user()
        self.login_user(user, "p1", expected_status=401)
        self.login_user(user, "p2", expected_status=200)

    def test_change_email(self, mail, user):
        self.login_user(user)

        with mail.record_messages() as outbox:
            r = self.post(f"/user/{user.id}", json={"email": "other@email.com"})
            assert r.status_code == 200, r.json
            assert len(outbox) == 1
            token = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        self.logout_user()

        r = self.login_user(user)
        assert r.json["user"]["email"] == user.email  # not yet validated

        r = self.post("/validate_email", json={"name": user.name, "token": token})
        assert r.status_code == 200, r.json

        r = self.get(f"/user/{user.id}")
        assert r.status_code == 200, r.json
        assert r.json["user"]["email"] == "other@email.com", r.json

    def test_errors(self, user, user_2):
        self.login_user(user)

        r = self.post(f"/user/{user_2.id}", json={"password": "p2"})
        assert r.status_code == 403, r.json
        assert r.json["description"] == "You can't modify this user"

    def test_email_error(self, user):
        self.login_user(user)

        r = self.post(f"/user/{user.id}", json={"email": None, "password": "p"})
        assert r.status_code == 400, r.json
        r = self.post(f"/user/{user.id}", json={"email": "", "password": "p"})
        assert r.status_code == 400, r.json
        r = self.post(f"/user/{user.id}", json={"email": "a.fr", "password": "p"})
        assert r.status_code == 400, r.json


class Test_UserUniqueness(BaseTest):
    def test_username(self, user):

        r = self.put("/users", json={"name": user.name, "email": "other@email.c", "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "A user still exists with this name"

    def test_email_at_creation(self, user):

        r = self.put("/users", json={"name": "other_name", "email": user._email, "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "A user still exists with this email"

    def test_email_at_modification(self, user, user_2):

        r = self.put("/users", json={"name": "other_user", "email": user._email, "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "A user still exists with this email"

        self.login_user(user)
        r = self.post(f"/user/{user.id}", json={"email": user_2._email})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "A user still exists with this email"

        r = self.post(f"/user/{user.id}", json={"email": "mail@competition.fr"})
        assert r.status_code == 200

        self.logout_user()

        self.login_user(user_2)
        r = self.post(f"/user/{user_2.id}", json={"email": "mail@competition.fr"})
        assert r.status_code == 200
        self.logout_user()

    def test_do_not_validate_same_email(self, mail):
        with mail.record_messages() as outbox:
            user1 = self.put("/users", json={"name": "user1", "email": "a@b.c", "password": "p"}).json["user"]
            token_1 = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        with mail.record_messages() as outbox:
            user2 = self.put("/users", json={"name": "user2", "email": "a@b.c", "password": "p"}).json["user"]
            token_2 = re.sub(r"^(.*email_token=)", "", outbox[0].body)

        r = self.post("/validate_email", json={"name": user1["name"], "token": token_1})
        assert r.status_code == 200, r.json

        r = self.post("/validate_email", json={"name": user2["name"], "token": token_2})
        assert r.status_code == 400, r.json
        assert r.json["description"] == "A user still exists with this email"


class Test_Logout(BaseTest):
    def test_main(self, user):
        self.logout_user(403)
        self.login_user(user)
        self.logout_user()
        self.logout_user(403)
