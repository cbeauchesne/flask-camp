from cms import database


class Test_UserCreation:
    # login should respond 403 / user is not validated

    # def test_wrong_input(self, client):
    # response = client.put("/create_user", json={})

    # assert response.status_code == 400
    # assert response.json["status"] == "error"
    # assert response.json["message"] == "error"

    def test_user_creation(self, client):
        response = client.put(
            "/create_user", json={"username": "my first user", "email": "a@b.c", "password": "weak password"}
        )
        assert response.status_code == 200
        assert response.json["status"] == "ok"

        user = response.json["user"]

        assert len(user) == 4, user
        assert "id" in user
        assert "ui_preferences" in user
        assert user["username"] == "my first user"
        assert user["email"] == "a@b.c"

        return user

    def test_typical_scenario(self, client):
        user = self.test_user_creation(client)
        user_id = user["id"]

        users = database._connection.execute(f"SELECT validation_token FROM user WHERE id={user_id}")
        token = [user for user in users][0]["validation_token"]

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert response.status_code == 200
        assert response.json["status"] == "ok"

        response = client.post("/login", json={"user_id": user_id, "password": "weak password"})
        assert response.status_code == 200

        response = client.get("/logout")
        assert response.status_code == 200

    def test_errors_on_token_validation(self, client):
        user = self.test_user_creation(client)
        user_id = user["id"]

        users = database._connection.execute(f"SELECT validation_token FROM user WHERE id={user_id}")
        token = [user for user in users][0]["validation_token"]

        response = client.get(f"/validate_user/{user_id}")
        assert response.status_code == 400
        assert (
            response.json["message"] == "The browser (or proxy) sent a request that this server could not understand."
        )

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": "not the good token"})
        assert response.status_code == 400
        assert response.json["message"] == "Token doesn't match"

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert response.status_code == 200

        response = client.get(f"/validate_user/{user_id}", query_string={"validation_token": token})
        assert response.status_code == 400
        assert response.json["message"] == "User is still validated"
