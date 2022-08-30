from tests.conftest import client


class Test_HealthCheck:
    def test_main(self, client):
        response = client.get("/healthcheck")
        assert response.status_code == 200
        assert response.json["status"] == "ok"
