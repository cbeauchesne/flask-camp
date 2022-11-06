from flask_camp._utils import JsonResponse


def test_main():
    r = JsonResponse({})

    assert hasattr(r, "data")
    assert hasattr(r, "add_etag")
    assert hasattr(r, "headers")
    assert hasattr(r, "status")

    assert r.status == 200
