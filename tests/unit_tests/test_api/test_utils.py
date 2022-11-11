from flask_camp import utils


def test_main():
    assert hasattr(utils, "JsonResponse")
    assert hasattr(utils, "SchemaValidator")
