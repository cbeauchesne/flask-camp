from functools import wraps
import logging
import json
import os

from flask import request, current_app
from jsonschema import Draft7Validator, RefResolver
from werkzeug.exceptions import BadRequest


class SchemaValidator:
    def __init__(self, base_dir):
        store = {}
        self._validators = {}

        if base_dir[-1] != "/":
            base_dir = f"{base_dir}/"

        if not os.path.isdir(base_dir):
            raise FileNotFoundError(f"{base_dir} is not a directory")

        BASE_URI = "https://schemas/"

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".json"):
                    filename = os.path.join(root, file)

                    with open(filename, encoding="utf8") as file:
                        data = json.load(file)

                    Draft7Validator.check_schema(data)

                    data["$id"] = filename[len(base_dir) :]
                    store[f"{BASE_URI}{filename[len(base_dir):]}"] = data

        for filename, data in store.items():
            resolver = RefResolver(base_uri=BASE_URI, referrer=data, store=store)
            self._validators[filename[len(BASE_URI) :]] = Draft7Validator(
                data, resolver=resolver, format_checker=Draft7Validator.FORMAT_CHECKER
            )

    def validate(self, data, *filenames):
        for filename in filenames:
            validator = self._validators[filename]
            errors = list(validator.iter_errors(data))

            if len(errors) != 0:
                messages = []

                for error in errors:
                    messages.append(f"{error.message} on instance " + "".join([f"[{repr(i)}]" for i in error.path]))

                raise BadRequest("\n".join(messages))

    def schema(self, filename):
        if not self.exists(filename):
            raise FileNotFoundError(f"{filename} does not exists")

        def decorator(real_method):
            @wraps(real_method)
            def wrapper(*args, **kwargs):
                current_app.logger.debug("Validate %s with %s", request.url_rule, filename)
                self.validate(request.get_json(), filename)

                return real_method(*args, **kwargs)

            return wrapper

        return decorator

    def exists(self, filename):
        return filename in self._validators


# expose a decorator for internal schema validation
schema = SchemaValidator(os.path.dirname(__file__)).schema
