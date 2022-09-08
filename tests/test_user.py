from tests.utils import BaseTest


class Test_UserCreation(BaseTest):
    def test_typical_scenario(self, client):
        name, password = "my user", "week password"

        response = client.put("/users", json={"name": name, "email": "a@b.c", "password": password})
        assert response.status_code == 200, response.json
        assert response.json["status"] == "ok"

        user = response.json["user"]

        assert len(user) == 5, user
        assert "id" in user
        assert "ui_preferences" in user
        assert user["name"] == name
        assert user["email"] == None
        assert user["roles"] == []

        user_id, token = self.get_validation_token(name)

        assert token is not None

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert response.status_code == 200
        assert response.json["status"] == "ok"

        response = self.login_user(client, name, password)
        assert response.status_code == 200
        assert response.json["status"] == "ok"

        user = response.json["user"]

        assert len(user) == 5, user
        assert user["id"] == user_id
        assert user["ui_preferences"] == None
        assert user["name"] == name
        assert user["email"] == "a@b.c"
        assert user["roles"] == []

        response = client.get("/logout")
        assert response.status_code == 200

    def test_errors_on_token_validation(self, client):
        name, password = "my user", "week password"
        user = self.add_user(name=name, password=password, validate_email=False)

        response = self.login_user(client, name, password, 401)
        assert response.json["message"] == "User's email is not validated"

        response = client.get(f"/validate_user/{user.id}")
        assert response.status_code == 400
        assert (
            response.json["message"] == "The browser (or proxy) sent a request that this server could not understand."
        )

        response = client.get(f"/validate_user/{user.id}", query_string={"validation_token": "not the good token"})
        assert response.status_code == 400
        assert response.json["message"] == "Token doesn't match"

        response = self.login_user(client, name, password, 401)
        assert response.json["message"] == "User's email is not validated"

        response = client.get(f"/validate_user/{user.id}", query_string={"validation_token": user.validation_token})
        assert response.status_code == 200

        response = client.get(f"/validate_user/{user.id}", query_string={"validation_token": user.validation_token})
        assert response.status_code == 400
        assert response.json["message"] == "User is still validated"

        response = self.login_user(client, name, password)
        assert response.status_code == 200

    def test_login_errors(self, client):
        password = "week password"
        user = self.add_user(password=password)

        response = self.login_user(client, "not the name", password, expected_status=400)
        assert response.json["message"] == "User does not exists, or password is wrong"

        response = self.login_user(client, user.name, "not the password", expected_status=400)
        assert response.json["message"] == "User does not exists, or password is wrong"

    def test_logout_errors(self, client):
        response = client.get("/logout")
        assert response.status_code == 401

    def test_get_errors(self, client):
        r = client.get(f"/user/1")
        assert r.status_code == 404


class Test_UserModification(BaseTest):
    def test_change_password(self, client):
        user = self.add_user(password="p1")
        self.login_user(client, user.name, "p1")

        r = client.post(f"/user/{user.id}", json={"password": "p2"})
        assert r.status_code == 200, r.json

        client.get("/logout")
        self.login_user(client, user.name, "p1", expected_status=400)
        self.login_user(client, user.name, "p2", expected_status=200)

    def test_change_email(self, client):
        user = self.add_user()
        self.login_user(client)

        r = client.post(f"/user/{user.id}", json={"email": "other@email.com"})
        assert r.status_code == 200, r.json

        client.get("/logout")

        r = self.login_user(client)
        assert r.json["user"]["email"] == user.email  # not yet validated

    def test_errors(self, client):
        user = self.add_user()
        other_user = self.add_user("other user")
        self.login_user(client)

        r = client.post(f"/user/{other_user.id}", json={"password": "p2"})
        assert r.status_code == 401, r.json
        assert r.json["message"] == "You can't modify this user"


class Test_UserUniqueness(BaseTest):
    def test_username(self, client):
        user = self.add_user()

        r = client.put("/users", json={"name": user.name, "email": "other@email.c", "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this name"

    def test_email(self, client):
        user = self.add_user()

        r = client.put("/users", json={"name": "other user", "email": user.email, "password": "x"})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this email"

        other_user = self.add_user(name="other_user")

        self.login_user(client)
        r = client.post(f"/user/{user.id}", json={"email": other_user.email})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this email"

        r = client.post(f"/user/{user.id}", json={"email": "mail@competition.fr"})
        assert r.status_code == 200

        client.get("/logout")

        self.login_user(client, name=other_user.name)
        r = client.post(f"/user/{other_user.id}", json={"email": "mail@competition.fr"})
        assert r.status_code == 200
        client.get("/logout")

        user_id, token = self.get_validation_token(other_user.name)
        r = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert r.status_code == 200
        assert r.json["status"] == "ok"

        user_id, token = self.get_validation_token(user.name)
        r = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert r.status_code == 400, r.json
        assert r.json["message"] == "A user still exists with this email"
