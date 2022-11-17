import pytest

from flask_camp.utils import SchemaValidator


def test_error():

    # user schema does not exists
    with pytest.raises(FileNotFoundError) as e:
        v = SchemaValidator("tests/unit_tests/schemas/")
        v.assert_schema_exists("notfound.json")
    assert e.match("File tests/unit_tests/schemas/notfound.json does not exists")

    # schemas_directory does not exists
    with pytest.raises(FileNotFoundError) as e:
        SchemaValidator("tests/not_a_dir/")
    assert e.match("tests/not_a_dir/ is not a directory")

    with pytest.raises(ValueError) as e:
        SchemaValidator("tests/unit_tests/schemas_with_error")
    assert e.match("JSON syntax error in tests/unit_tests/schemas_with_error/outing.json")
