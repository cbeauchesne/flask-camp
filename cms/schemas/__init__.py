import os
import json

from flask import request
from flask_restful import abort
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker


def schema(filename):
    if filename not in _validators:
        raise FileNotFoundError(f"{filename} does not exists")

    validator = _validators[filename]

    def decorator(real_method):
        def wrapper(*args, **kwargs):
            print(f"Validate {request.url_rule} with {filename}")

            data = request.get_json()
            errors = list(validator.iter_errors(data))

            if len(errors) != 0:
                messages = []

                for error in errors:
                    messages.append(f"{error.message} on instance " + "".join([f"[{repr(i)}]" for i in error.path]))

                print("\n".join(messages))
                abort(400, message="\n".join(messages))

            return real_method(*args, **kwargs)

        return wrapper

    return decorator


_validators = {}
_store = {}


def _init():

    for dir in ("cms/schemas/",):
        for root, _, files in os.walk(dir):
            for f in files:
                if f.endswith(".json"):
                    filename = os.path.join(root, f)
                    schema = json.load(open(filename))
                    Draft7Validator.check_schema(schema)

                    if "$id" in schema:
                        _store[schema["$id"]] = schema

            for f in files:
                if f.endswith(".json"):
                    filename = os.path.join(root, f)
                    resolver = RefResolver(base_uri=schema["$id"], referrer=schema, store=_store)
                    _validators[filename] = Draft7Validator(
                        schema, resolver=resolver, format_checker=draft7_format_checker
                    )
                    print(f"Compiling schemas {filename}")


_init()
