from tests.unit_tests.utils import BaseTest


class Test_Home(BaseTest):
    def test_main(self):
        response = self.get("/")
        assert response.status_code == 200

        for entry_point in response.json:
            for method in response.json[entry_point]:
                data = response.json[entry_point][method]
                assert data["description"] is not None, f"Docstring is not set for {method} {entry_point}"
