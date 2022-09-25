from tests.unit_tests.utils import BaseTest


class Test_Home(BaseTest):
    def test_main(self):
        response = self.get("/")
        assert response.status_code == 200
