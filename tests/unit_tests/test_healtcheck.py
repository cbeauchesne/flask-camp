from tests.unit_tests.utils import BaseTest


class Test_HealthCheck(BaseTest):
    def test_main(self):
        response = self.get("/healthcheck")
        assert response.status_code == 200
        assert response.json["status"] == "ok"
