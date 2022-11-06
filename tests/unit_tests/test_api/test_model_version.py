from flask_camp.models import DocumentVersion


def test_data():
    version = DocumentVersion(data=None)
    assert version._data == "null"

    version.data = {"hello": "world"}
    assert version._data == '{"hello": "world"}'
