from flask_camp._utils import JsonResponse
from tests.unit_tests.utils import BaseTest


def test_main():
    r = JsonResponse({})

    assert hasattr(r, "data")
    assert hasattr(r, "add_etag")
    assert hasattr(r, "headers")
    assert hasattr(r, "status")

    assert r.status == 200


def after_get_document(response: JsonResponse):
    response.add_etag = False
    response.headers["x-test"] = "done"


class Test_AfterGetDocument(BaseTest):
    rest_api_kwargs = {
        "after_get_document": after_get_document,
    }

    def test_main(self, user):
        self.login_user(user)

        doc = self.create_document().json["document"]

        r = self.get_document(doc)
        assert "ETag" not in r.headers
        assert "x-test" in r.headers
        assert r.headers["x-test"] == "done"
