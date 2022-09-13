from tests.utils import BaseTest


class Test_Errors(BaseTest):
    def test_main(self):
        r = self.get("/do_not_exists")
        assert r.status_code == 404
        assert r.json is not None
        assert r.json["status"] == "error"

        r = self.delete("/healthcheck")
        assert r.status_code == 405
        assert r.json is not None
        assert r.json["status"] == "error"
