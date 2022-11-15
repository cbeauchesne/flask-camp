from collections import defaultdict
import json
import re

from flask import Flask

from flask_camp import RestApi
from flask_camp.__main__ import main
from flask_camp.client import ClientInterface


class BaseTest(ClientInterface):
    client = None
    rest_api_kwargs = {}
    rest_api_decorated = {}

    @classmethod
    def setup_class(cls):
        cls.app = Flask(__name__, static_folder=None)
        cls.app.config.update(
            {"TESTING": True, "SECRET_KEY": "not very secret", "SQLALCHEMY_TRACK_MODIFICATIONS": False}
        )

        cls.api = RestApi(app=cls.app, **cls.rest_api_kwargs)

        for name, argument in cls.rest_api_decorated.items():
            decorator = getattr(cls.api, name)
            decorator(argument)

    def setup_method(self):
        with self.app.app_context():
            self.api.database.create_all()

        with self.app.test_client() as client:
            self.client = client

    def teardown_method(self):
        with self.app.app_context():
            self.api.database.drop_all()

        self.api.memory_cache.flushall()

    @staticmethod
    def _convert_kwargs(kwargs):
        """convert request argument to flask test client argument"""
        kwargs["query_string"] = kwargs.pop("params", None)

    def get(self, url, **kwargs):
        expected_status = kwargs.pop("expected_status", 200)
        self._convert_kwargs(kwargs)

        r = self.client.get(url, **kwargs)
        self.assert_status_code(r, expected_status)

        return r

    def post(self, url, **kwargs):
        expected_status = kwargs.pop("expected_status", 200)
        self._convert_kwargs(kwargs)

        r = self.client.post(url, **kwargs)
        self.assert_status_code(r, expected_status)

        return r

    def put(self, url, **kwargs):
        expected_status = kwargs.pop("expected_status", 200)
        self._convert_kwargs(kwargs)

        r = self.client.put(url, **kwargs)
        self.assert_status_code(r, expected_status)

        return r

    def delete(self, url, **kwargs):
        expected_status = kwargs.pop("expected_status", 200)
        self._convert_kwargs(kwargs)

        r = self.client.delete(url, **kwargs)
        self.assert_status_code(r, expected_status)

        return r

    @staticmethod
    def assert_status_code(response, expected_status):
        if expected_status is None:
            expected_status = [200]
        elif isinstance(expected_status, int):
            expected_status = [expected_status]

        assert (
            response.status_code in expected_status
        ), f"Status error: {response.status_code} i/o {expected_status}\n{response.data}"

    def _assert_status_response(self, r):
        if r.status_code == 304:  # not modified : no body
            assert r.data == b""
        elif r.status_code == 301:  # Moved permanently : no body
            assert r.data == b""
            assert "Location" in r.headers
        else:
            assert r.json is not None, r.data
            assert "status" in r.json, r.json

            if r.status_code == 200:
                assert r.json["status"] == "ok", r.json
            else:
                assert r.json["status"] == "error", r.json
                assert "description" in r.json, r.json

    def assert_document_schema(self, document):

        print("Document is:")
        print(json.dumps(document, indent=4))

        expected_count = 10 if "cooked" in document else 9
        assert len(document) == expected_count, list(document.keys())
        assert "data" in document
        assert isinstance(document["id"], int)
        assert isinstance(document["comment"], str)
        assert isinstance(document["version_id"], int)
        assert isinstance(document["timestamp"], str)
        assert isinstance(document["hidden"], bool)
        assert isinstance(document["protected"], bool)
        assert isinstance(document["version_id"], int)
        assert isinstance(document["user"], dict)

        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00", document["timestamp"])

        self.assert_user_schema(document["user"], include_personal_data=False)

    def assert_user_schema(self, user, include_personal_data):
        print("User is:")
        print(json.dumps(user, indent=4))

        expected_count = 7 if include_personal_data else 5
        assert len(user) == expected_count, list(user.keys())
        assert isinstance(user["id"], int)
        assert isinstance(user["name"], str)
        assert isinstance(user["creation_date"], str)
        assert isinstance(user["blocked"], bool)
        assert isinstance(user["roles"], list)
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00", user["creation_date"])

        if include_personal_data:
            assert isinstance(user["email"], str)
            assert "data" in user

    ######

    def create_user(self, name="user", email=None, password="password", data=None, **kwargs):
        email = f"{name}@example.com" if email is None else email
        r = super().create_user(name, email, password, data=data, **kwargs)
        if r.status_code == 200:
            self.assert_user_schema(r.json["user"], include_personal_data=False)

        return r

    def login_user(self, user, password=None, token=None, **kwargs):
        if password is None and token is None:
            password = "password"

        r = super().login_user(user, password=password, token=token, **kwargs)
        if r.status_code == 200:
            self.assert_user_schema(r.json["user"], include_personal_data=True)

        return r

    def block_user(self, user, comment="Default comment", **kwargs):
        return super().block_user(user, comment, **kwargs)

    def unblock_user(self, user, comment="Default comment", **kwargs):
        return super().unblock_user(user, comment, **kwargs)

    def create_document(self, data=None, comment="Default comment", **kwargs):
        result = super().create_document(data={} if data is None else data, comment=comment, **kwargs)
        if result.status_code == 200:
            self.assert_document_schema(result.json["document"])

        return result

    def modify_document(self, document, comment="Default comment", data=None, **kwargs):
        data = data if data is not None else document["data"]
        result = super().modify_document(document, comment, data, **kwargs)

        if result.status_code == 200:
            self.assert_document_schema(result.json["document"])

        return result

    def get_document(
        self,
        document,
        data_should_be_present=True,
        version_should_be=None,
        **kwargs,
    ):
        r = super().get_document(document, **kwargs)

        if r.status_code == 200:
            if data_should_be_present:
                assert "data" in r.json["document"]
            else:
                assert "data" not in r.json["document"]

            if version_should_be:
                assert r.json["document"]["version_id"] == version_should_be["version_id"], r.json["document"]

            self.assert_document_schema(r.json["document"])

        return r

    def get_documents(self, limit=None, offset=None, tag_name=None, tag_user=None, tag_value=None, **kwargs):
        r = super().get_documents(limit, offset, tag_name, tag_user, tag_value, **kwargs)
        if r.status_code == 200:
            for document in r.json["documents"]:
                self.assert_document_schema(document)

        return r

    def protect_document(self, document, comment="Default comment", **kwargs):
        return super().protect_document(document, comment, **kwargs)

    def unprotect_document(self, document, comment="Default comment", **kwargs):
        return super().unprotect_document(document, comment, **kwargs)

    def merge_documents(self, document_to_merge, document_destination, comment="Default comment", **kwargs):
        return super().merge_documents(document_to_merge, document_destination, comment, **kwargs)

    def delete_document(self, document, comment="Default comment", **kwargs):
        return super().delete_document(document, comment, **kwargs)

    def get_version(self, version, data_should_be_present=True, **kwargs):
        r = super().get_version(version, **kwargs)

        if r.status_code == 200:
            if data_should_be_present:
                assert "data" in r.json["document"]
            else:
                assert "data" not in r.json["document"]

        return r

    def hide_version(self, version, comment="Default comment", **kwargs):
        return super().hide_version(version, comment, **kwargs)

    def unhide_version(self, version, comment="Default comment", **kwargs):
        return super().unhide_version(version, comment, **kwargs)

    def delete_version(self, version, comment="Default comment", **kwargs):
        return super().delete_version(version, comment, **kwargs)

    def rename_user(self, user, name, comment="Default comment", **kwargs):
        return super().rename_user(user, name, comment, **kwargs)

    @staticmethod
    def cli_main(args):
        args = defaultdict(lambda: False, **args)
        main(args)
