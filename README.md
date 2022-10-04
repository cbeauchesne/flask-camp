## Install

``` bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade setuptools pip
pip install -e .
pip install -r dev-requirements.txt
```

## Dev env

In a separated terminal, start the dev env : 

``` bash
./scripts/start_dev_env.sh
```


## Unit tests

``` bash
pytest
```
