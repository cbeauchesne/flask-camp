This folder will contains any helpful information to modify Flask-Camp project

## How to modify the project

You will need `docker` and `python`. Once you've clone the repo, install the dev env : 

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade setuptools pip
pip install -e .
pip install -r dev-requirements.txt
```

Then, before any modification, you'll need to activate the python virtual env : 

```bash
source venv/bin/activate
```

And you'll need a redis and postgresql reaady to accept connection. You can easily do that with this command 

```bash
./scripts/start_dev_env.sh
```

That's done, you can start your modification

## Unit tests

At the root folder of the repo :

```bash
# Run the default test scenario:
pytest

# Run a test file
pytest tests/unit_tests/test_document.py

# Run a test class
pytest tests/unit_tests/test_document.py::Test_Document

# Run a test method
pytest tests/unit_tests/test_document.py::Test_Document::test_deletion

# see verbose output
pytest -v

# see very verbose output, even with SQL queries
pytest -vv
```
