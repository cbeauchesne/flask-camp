from collections import defaultdict

from flask_camp.__main__ import main
from tests.unit_tests.utils import BaseTest


def cli_main(args):
    args = defaultdict(lambda: False, **args)
    main(args)


class Test_CLI(BaseTest):
    def test_main(self):
        with self.app.app_context():
            self.api.database.drop_all()

        cli_main({"init_db": True})
        cli_main({"add_admin": True, "<name>": "admin", "<email>": "admin@email.com", "<password>": "blah"})

        user = self.login_user("admin", password="blah").json["user"]

        assert user["email"] == "admin@email.com"
