from cms import database
from tests.utils import BaseTest


class Test_UserCreation(BaseTest):
    def test_typical_scenario(self, client):
        username, password = "my user", "week password"

        response = client.put("/users", json={"username": username, "email": "a@b.c", "password": password})
        assert response.status_code == 200, response.json
        assert response.json["status"] == "ok"

        user = response.json["user"]

        assert len(user) == 4, user
        assert "id" in user
        assert "ui_preferences" in user
        assert user["username"] == username
        assert user["email"] == "a@b.c"

        user_id = user["id"]

        users = database.execute(f"SELECT id, validation_token FROM user WHERE username='{username}'")
        user = [user for user in users][0]

        token = user["validation_token"]
        user_id = user["id"]

        assert token is not None

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})

        assert response.status_code == 200
        assert response.json["status"] == "ok"

        users = database.execute(f"SELECT validation_token FROM user WHERE username='{username}'")
        token = [user for user in users][0]["validation_token"]
        assert token is None

        response = self.login_user(client, username, password)
        assert response.status_code == 200
        assert response.json["status"] == "ok"

        user = response.json["user"]

        assert len(user) == 4, user
        assert user["id"] == user_id
        assert user["ui_preferences"] == None
        assert user["username"] == username
        assert user["email"] == "a@b.c"

        response = client.get("/logout")
        assert response.status_code == 200

    def test_errors_on_token_validation(self, client):
        username, password = "my user", "week password"
        user = self.add_user(username, password, validate_email=False)

        response = client.get(f"/validate_user/{user.id}")
        assert response.status_code == 400
        assert (
            response.json["message"] == "The browser (or proxy) sent a request that this server could not understand."
        )

        response = client.get(f"/validate_user/{user.id}", query_string={"validation_token": "not the good token"})
        assert response.status_code == 400
        assert response.json["message"] == "Token doesn't match"

        response = self.login_user(client, username, password, 401)
        assert response.json["message"] == "User is not validated"

        response = client.get(f"/validate_user/{user.id}", query_string={"validation_token": user.validation_token})
        assert response.status_code == 200

        response = client.get(f"/validate_user/{user.id}", query_string={"validation_token": user.validation_token})
        assert response.status_code == 400
        assert response.json["message"] == "User is still validated"

        response = self.login_user(client, username, password)
        assert response.status_code == 200

    def test_login_errors(self, client):
        password = "week password"
        user = self.add_user("my user", password)

        response = self.login_user(client, "not the username", password, expected_status=400)
        assert response.json["message"] == "User does not exists, or password is wrong"

        response = self.login_user(client, user.username, "not the password", expected_status=400)
        assert response.json["message"] == "User does not exists, or password is wrong"

    def test_logout_errors(self, client):
        response = client.get("/logout")
        assert response.status_code == 401
