from freezegun import freeze_time
from flask_login import current_user

from flask_camp import allow

from tests.unit_tests.utils import BaseTest


class RateLimitedClass:
    rule = "/rate_limited"

    @allow("anonymous")
    def get(self):
        """I'm rate limited"""
        return {"hello": "world"}


class Test_RateLimit(BaseTest):
    rest_api_kwargs = {
        "rate_limit_cost_function": lambda: 0 if current_user.is_admin else 1,
        "rate_limits_file": "tests/ratelimit_config.json",
    }

    def test_rate_limited_class_instance(self):

        self.api.add_modules(self.app, RateLimitedClass())

        results = []
        with freeze_time():
            for _ in range(6):
                r = self.get("/rate_limited", expected_status=(200, 429))
                results.append(r.status_code)

        assert results[0] == results[1] == results[2] == results[3] == results[4] == 200
        assert results[5] == 429

    def test_main(self):
        results = []
        with freeze_time():
            for _ in range(6):
                r = self.get("/", environ_base={"REMOTE_ADDR": "127.0.0.2"}, expected_status=(200, 429))
                results.append(r.status_code)

        assert results[0] == results[1] == results[2] == results[3] == results[4] == 200
        assert results[5] == 429

    def test_rate_limit_cost(self, admin):

        results = []

        self.login_user(admin)
        with freeze_time():
            for _ in range(6):
                r = self.get("/", environ_base={"REMOTE_ADDR": "127.0.0.2"}, expected_status=(200, 429))
                results.append(r.status_code)

        assert results[0] == results[1] == results[2] == results[3] == results[4] == results[5] == 200

    def test_info(self):
        routes = self.get("/").json
        assert routes["/"]["GET"].get("rate_limit") == "5 per second", routes["/"]["GET"]
