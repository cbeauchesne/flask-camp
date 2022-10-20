from tests.unit_tests.utils import BaseTest


class Test_CLI(BaseTest):
    def test_main(self):
        with self.app.app_context():
            self.api.database.drop_all()

        self.cli_main({"init_db": True})
        self.cli_main({"add_admin": True, "<name>": "admin", "<email>": "admin@email.com", "<password>": "blah"})

        user = self.login_user("admin", password="blah").json["user"]

        assert user["email"] == "admin@email.com"
