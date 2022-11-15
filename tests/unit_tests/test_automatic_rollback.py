from werkzeug.exceptions import BadRequest

from flask_camp.models import User

from tests.unit_tests.utils import BaseTest


def before_update_user(user):
    user.name = "not the good name"
    raise BadRequest()


class Test_AutomaticRollback(BaseTest):
    rest_api_decorated = {
        "before_update_user": before_update_user,
    }

    def test_main(self, user):
        def check(r):
            updated_user = self.api.database.session.query(User).get(user.id)
            assert updated_user.name != "not the good name"
            return r

        self.app.after_request(check)

        self.login_user(user)
        self.modify_user(user, expected_status=400)
