import sys

import requests
from sqlalchemy import create_engine

from tests.utils import ClientInterface


engine = create_engine("postgresql://cms_user:cms_user@localhost:5432/cms")


def get_email_token(user_name):
    with engine.connect() as connection:
        rows = connection.execute(f"SELECT email_token FROM user_account WHERE name='{user_name}'")
        token = list(rows)[0][0]
        return token


class ClientSession(ClientInterface):
    _session_id = 0

    def __init__(self, domain):
        self.domain = domain
        self._session = requests.Session()
        self.logged_user = None
        ClientSession._session_id += 1  # TODO thread lock
        self.session_id = ClientSession._session_id

    @property
    def logged_user_name(self):
        return "<anon>" if self.logged_user is None else self.logged_user["name"]

    def __str__(self):
        return f"S#{self.session_id} ({self.logged_user_name})"

    def _request(self, method, url, expected_status=None, **kwargs):
        print(f"{str(self):20} {method.upper():6} {url:30}")
        r = self._session.request(method, f"{self.domain}{url}", **kwargs, timeout=1)
        print(f"{str(self):20} {method.upper():6} {url:30} {r.status_code}")

        expected_status = 200 if expected_status is None else expected_status

        if expected_status != r.status_code:
            print(f"\tExpected status is: {expected_status}")
            print(f"\tContent is: {r.content}")
            sys.exit(1)

        return r

    def get(self, url, params=None, headers=None, expected_status=None):
        return self._request("get", url, params=params, headers=headers, expected_status=expected_status)

    def post(self, url, params=None, json=None, headers=None, expected_status=None):
        return self._request("post", url, params=params, headers=headers, json=json, expected_status=expected_status)

    def put(self, url, params=None, data=None, json=None, headers=None, expected_status=None):
        return self._request(
            "put", url, params=params, headers=headers, json=json, data=data, expected_status=expected_status
        )

    def delete(self, url, params=None, json=None, headers=None, expected_status=None):
        return self._request("delete", url, params=params, headers=headers, json=json, expected_status=expected_status)

    def login_user(self, user, password="password", token=None, expected_status=None):
        r = super().login_user(user, password=password, token=token, expected_status=expected_status)

        if r.status_code == 200:
            self.logged_user = r.json()["user"]

        return r

    def setup_user(self, name):
        self.create_user(name)
        self.validate_email(name, get_email_token(name))
        self.login_user(name)
