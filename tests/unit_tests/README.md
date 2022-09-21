At the root folder of the repo :

```bash
# Run the default test scenario:
pytest

# Run a test file
pytest cms/views/protect_document.py

# Run a test class
pytest cms/views/test_document.py::Test_Document

# Run a test method
pytest cms/unit_tests/test_document.py::Test_Document::test_deletion

# see verbose output
pytest -v

# see very verbose output, even with SQL queries
pytest -vv
```