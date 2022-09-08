from tests.utils import BaseTest


class Test_UserCreation(BaseTest):
    def test_typical_scenario(self):
        name, email, password = "my user", "a@b.c", "week password"

        r = self.put("/users", json={"name": name, "email": email, "password": password})
        assert r.status_code == 200, r.json
        assert r.json["status"] == "ok"

        user = r.json["user"]

        assert len(user) == 5, user
        assert "id" in user
        assert "ui_preferences" in user
        assert user["blocked"] == False
        assert user["name"] == name
        assert user["roles"] == []

        token = self.get_email_token(name)
        assert token is not None

        r = self.post(f"/validate_email", json={"name": name, "token": token})
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
        assert r.json["user"]["blocked"] == False
        assert r.json["user"]["ui_preferences"] == None
        assert r.json["user"]["name"] == name
        assert r.json["user"]["email"] == email
        assert r.json["user"]["roles"] == []

        r = self.logout_user()

    def test_errors_on_token_validation(self):
        password = "weak password"
        user = self.add_user(password=password, validate_email=False)

        r = self.login_user(password=password, expected_status=401)
        assert r.json["message"] == "User's email is not validated"

        r = self.post(f"/validate_email", json={"name": user.name})
        assert r.status_code == 400
        assert r.json["message"] == "'token' is a required property on instance "

        r = self.post(f"/validate_email", json={"name": "not the name", "token": user.email_token})
        assert r.status_code == 404

        r = self.post(f"/validate_email", json={"name": user.name, "token": "not the good one"})
        assert r.status_code == 401
        assert r.json["message"] == "Token doesn't match"

        r = self.login_user(user.name, password, expected_status=401)
        assert r.json["message"] == "User's email is not validated"

        r = self.post(f"/validate_email", json={"name": user.name, "token": user.email_token})
        assert r.status_code == 200

        r = self.post(f"/validate_email", json={"name": user.name, "token": user.email_token})
        assert r.status_code == 400
        assert r.json["message"] == "There is no email to validate"

        r = self.login_user(password=password, expected_status=200)

    def test_login_errors(self):
        password = "week password"
        user = self.add_user(password=password)

        r = self.login_user("not the name", password, expected_status=401)
        assert r.json["message"] == "User does not exists, or password is wrong"

        r = self.login_user(user.name, "not the password", expected_status=401)
        assert r.json["message"] == "User does not exists, or password is wrong"

        r = self.post("/login", json={"name": user.name})
        assert r.status_code == 400, r.json

    def test_logout_errors(self):
        r = self.get("/logout")
        assert r.status_code == 403

    def test_notfound_errors(self):
        user = self.add_user()
        self.login_user()
        r = self.get("/user/42")
        assert r.status_code == 404

    def test_anonymous_get(self):
        user = self.add_user()
        r = self.get(f"/user/{user.id}")
        assert r.status_code == 200


class Test_UserModification(BaseTest):
    def test_change_password(self):
        user = self.add_user(password="p1")
        self.login_user(user.name, "p1")

        r = self.post(f"/user/{user.id}", json={"password": "p2"})
        assert r.status_code == 200, r.json

        self.get("/logout")
        self.login_user(user.name, "p1", expected_status=401)
        self.login_user(user.name, "p2", expected_status=200)

    def test_change_email(self):
        user = self.add_user()
        self.login_user()

        r = self.post(f"/user/{user.id}", json={"email": "other@email.com"})
        assert r.status_code == 200, r.json

        self.logout_user()

        r = self.login_user()
        assert r.json["user"]["email"] == user.email  # not yet validated

        token = self.get_email_token(user.name)
        r = self.post("/validate_email", json={"name": user.name, "token": token})
        assert r.status_code == 200, r.json

        r = self.get(f"/user/{user.id}")
        assert r.status_code == 200, r.json
        assert r.json["user"]["email"] == "other@email.com", r.json

    def test_errors(self):
        user = self.add_user()
        other_user = self.add_user("other user")
        self.login_user()

        r = self.post(f"/user/{other_user.id}", json={"password": "p2"})
        assert r.status_code == 403, r.json
        assert r.json["message"] == "You can't modify this user"


class Test_UserUniqueness(BaseTest):
    def test_username(self):
        user = self.add_user()

        r = self.put("/users", json={"name": user.name, "email": "other@email.c", "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this name"

    def test_email_at_creation(self):
        user = self.add_user()

        r = self.put("/users", json={"name": "other name", "email": user._email, "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this email"

    def test_email_at_modification(self):
        user = self.add_user()

        r = self.put("/users", json={"name": "other user", "email": user._email, "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this email"

        other_user = self.add_user(name="other_user")

        self.login_user()
        r = self.post(f"/user/{user.id}", json={"email": other_user._email})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this email"

        r = self.post(f"/user/{user.id}", json={"email": "mail@competition.fr"})
        assert r.status_code == 200

        self.get("/logout")

        self.login_user(name=other_user.name)
        r = self.post(f"/user/{other_user.id}", json={"email": "mail@competition.fr"})
        assert r.status_code == 200
        self.get("/logout")

    def test_do_not_validate_same_email(self):
        user1 = self.add_user("u1", "a@b.c", validate_email=False)
        user2 = self.add_user("u2", "a@b.c", validate_email=False)

        r = self.post(f"/validate_email", json={"name": user1.name, "token": user1.email_token})
        assert r.status_code == 200, r.json

        r = self.post(f"/validate_email", json={"name": user2.name, "token": user2.email_token})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this email"


class Test_Logout(BaseTest):
    def test_main(self):
        self.logout_user(403)
        self.add_user()
        self.login_user()
        self.logout_user()
        self.logout_user(403)
