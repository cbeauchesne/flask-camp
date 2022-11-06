from flask_camp import RestApi


def test_main():
    api = RestApi()

    assert hasattr(api, "add_views")
    assert hasattr(api, "init_app")
    assert hasattr(api, "get_document")
    assert hasattr(api, "get_cooked_document")
