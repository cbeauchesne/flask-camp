from flask_camp.models import User
from tests.unit_tests.utils import BaseTest


class Test_UserLogin(BaseTest):
    def test_normalization(self):
        with self.app.app_context():
            user = User.create(name="  CaPiTaL  ", email="  CaPiTaL@example.com  ", password="x")

        assert user.name == "capital"
        assert user._email_to_validate == "capital@example.com"

    def test_name(self, user):
        self.put("/user/login", json={"name_or_email": user.name, "password": "password"}, expected_status=200)

    def test_name_capitalization(self, user):
        self.put("/user/login", json={"name_or_email": user.name.upper(), "password": "password"}, expected_status=200)
        self.put("/user/login", json={"name_or_email": user.name.lower(), "password": "password"}, expected_status=200)

    def test_email(self, user):
        self.put("/user/login", json={"name_or_email": user._email, "password": "password"}, expected_status=200)

    def test_email_capitalization(self, user):
        self.put(
            "/user/login", json={"name_or_email": user._email.upper(), "password": "password"}, expected_status=200
        )
        self.put(
            "/user/login", json={"name_or_email": user._email.lower(), "password": "password"}, expected_status=200
        )

    def test_login_errors(self, user):
        r = self.login_user("not_the_name", expected_status=401)
        assert r.json["description"] == "User does not exists, or password is wrong"

        r = self.login_user(user, password="not the password", expected_status=401)
        assert r.json["description"] == "User does not exists, or password is wrong"

        self.put("/user/login", json={"name_or_email": user.name}, expected_status=400)
