from tests.utils import BaseTest


class Test_Document(BaseTest):
    def test_main(self, client):
        r = client.get("/changes")
        assert r.status_code == 200
