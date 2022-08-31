from cms import database


class Test_UserCreation:
    # login should respond 403 / user is not validated

    # def test_wrong_input(self, client):
    # response = client.put("/create_user", json={})

    # assert response.status_code == 400
    # assert response.json["status"] == "error"
    # assert response.json["message"] == "error"

    def login_user(self, client, username, password):
        return client.post("/login", json={"username": username, "password": password})

    def create_user(self, client, username, password):
        response = client.put("/create_user", json={"username": username, "email": "a@b.c", "password": password})
        assert response.status_code == 200
        assert response.json["status"] == "ok"

        user = response.json["user"]

        assert len(user) == 4, user
        assert "id" in user
        assert "ui_preferences" in user
        assert user["username"] == username
        assert user["email"] == "a@b.c"

        return user

    def validate_user(self, client, username):
        users = database.execute(f"SELECT id, validation_token FROM user WHERE username='{username}'")
        user = [user for user in users][0]

        token = user["validation_token"]
        user_id = user["id"]

        assert token is not None

        return client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})

    def test_typical_scenario(self, client):
        username, password = "my user", "week password"
        user = self.create_user(client, username, password)
        user_id = user["id"]

        response = self.validate_user(client, username)
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
        user = self.create_user(client, username, password)
        user_id = user["id"]

        users = database.execute(f"SELECT validation_token FROM user WHERE id={user_id}")
        token = [user for user in users][0]["validation_token"]

        response = client.get(f"/validate_user/{user_id}")
        assert response.status_code == 400
        assert (
            response.json["message"] == "The browser (or proxy) sent a request that this server could not understand."
        )

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": "not the good token"})
        assert response.status_code == 400
        assert response.json["message"] == "Token doesn't match"

        response = self.login_user(client, username, password)
        assert response.status_code == 403
        assert response.json["message"] == "User is not validated"

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert response.status_code == 200

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert response.status_code == 400
        assert response.json["message"] == "User is still validated"

        response = self.login_user(client, username, password)
        assert response.status_code == 200

    def test_login_errors(self, client):
        username, password = "my user", "week password"
        user = self.create_user(client, username, password)
        self.validate_user(client, username)

        response = self.login_user(client, "no the username", password)
        assert response.status_code == 403
        assert response.json["message"] == "User does not exists, or password is wrong"

        response = self.login_user(client, username, "not the password")
        assert response.status_code == 403
        assert response.json["message"] == "User does not exists, or password is wrong"
