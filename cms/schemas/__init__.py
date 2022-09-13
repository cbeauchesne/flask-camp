from functools import wraps
import logging
import json
import os

from flask import request
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker
from werkzeug.exceptions import BadRequest


log = logging.getLogger(__name__)


def schema(filename):
    if filename not in _validators:
        raise FileNotFoundError(f"{filename} does not exists")

    validator = _validators[filename]

    def decorator(real_method):
        @wraps(real_method)
        def wrapper(*args, **kwargs):
            log.debug("Validate %s with %s", request.url_rule, filename)

            data = request.get_json()

            if data is None:
                raise BadRequest("Expecting JSON body")

            errors = list(validator.iter_errors(data))

            if len(errors) != 0:
                messages = []

                for error in errors:
                    messages.append(f"{error.message} on instance " + "".join([f"[{repr(i)}]" for i in error.path]))

                log.error("\n".join(messages))
                raise BadRequest("\n".join(messages))

            return real_method(*args, **kwargs)

        return wrapper

    return decorator


_validators = {}


def _init():

    store = {}

    for dir_name in ("cms/schemas/",):
        for root, _, files in os.walk(dir_name):
            for file in files:
                if file.endswith(".json"):
                    filename = os.path.join(root, file)

                    with open(filename, encoding="utf8") as file:
                        data = json.load(file)

                    Draft7Validator.check_schema(data)

                    data["$id"] = filename
                    store[f"https://schemas/{filename}"] = data

    for filename, data in store.items():
        resolver = RefResolver(base_uri="https://schemas/", referrer=data, store=store)
        log.debug("Compiling schemas %s", filename[16:])
        _validators[filename[16:]] = Draft7Validator(data, resolver=resolver, format_checker=draft7_format_checker)


_init()
