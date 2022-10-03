from freezegun import freeze_time

from tests.unit_tests.utils import BaseTest


class Test_RateLimit(BaseTest):
    def test_main(self):
        results = []
        with freeze_time():
            for _ in range(6):
                r = self.get("/", environ_base={"REMOTE_ADDR": "127.0.0.2"}, expected_status=(200, 429))
                results.append(r.status_code)

        assert results[0] == results[1] == results[2] == results[3] == results[4] == 200
        assert results[5] == 429

        routes = self.get("/").json

        assert routes["/"]["GET"].get("rate_limit") == "5 per second", routes["/"]["GET"]
