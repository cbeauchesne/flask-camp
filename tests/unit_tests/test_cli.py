import subprocess
from tests.unit_tests.utils import BaseTest


class Test_CLI(BaseTest):
    def test_main(self):
        with self.app.app_context():
            self.api.database.drop_all()

        subprocess.run(["flask", "init-db"], check=True)
        subprocess.run(["flask", "add-admin", "admin", "blah", "admin@email.com"], check=True)

        user = self.login_user("admin", password="blah").json["user"]

        assert user["email"] == "admin@email.com"
