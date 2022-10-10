import collections
from time import perf_counter

import requests
from sqlalchemy import create_engine

from flask_camp.client import ClientInterface


engine = create_engine("postgresql://flask_camp_user:flask_camp_user@localhost:5432/flask_camp")


def get_email_token(user_name):
    with engine.connect() as connection:
        rows = connection.execute(f"SELECT email_token FROM user_account WHERE name='{user_name}'")
        token = list(rows)[0][0]
        return token


class ClientSession(ClientInterface):
    _session_id = 0

    def __init__(self, domain="http://localhost:5000"):
        self.domain = domain
        self._session = requests.Session()
        self.logged_user = None
        ClientSession._session_id += 1  # TODO thread lock
        self.session_id = ClientSession._session_id
        self.stats = collections.defaultdict(list)

    @property
    def logged_user_name(self):
        return "<anon>" if self.logged_user is None else self.logged_user["name"]

    def __str__(self):
        return f"S#{self.session_id} ({self.logged_user_name})"

    def add_stat(self, method, url, outcome, ellapsed):
        key = (method.upper(), url.split("/")[1], outcome)
        self.stats[key].append(ellapsed)

    def _request(self, method, url, **kwargs):
        outcome = None

        expected_status = kwargs.pop("expected_status", None)

        start = perf_counter()
        try:
            r = self._session.request(method, f"{self.domain}{url}", **kwargs, timeout=10)
            outcome = str(r.status_code)
        except Exception as e:
            outcome = str(e)
            raise
        finally:
            ellapsed = (perf_counter() - start) * 1000
            self.add_stat(method, url, outcome, ellapsed)

        expected_status = 200 if expected_status is None else expected_status

        expected_status = expected_status if isinstance(expected_status, (list, tuple, set)) else [expected_status]

        if r.status_code not in expected_status:
            print(f"{method.upper()} {url}")
            print(f"Params: {kwargs.get('params')}")
            print(f"Expected status: {expected_status}")
            print(f"Observed status: {r.status_code}")
            print(f"Headers: {r.headers}")
            print(f"Content: {r.content}")
            raise ValueError()

        return r

    def get(self, url, **kwargs):
        return self._request("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self._request("post", url, **kwargs)

    def put(self, url, **kwargs):
        return self._request("put", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request("delete", url, **kwargs)

    def login_user(self, user, password="password", token=None, **kwargs):
        r = super().login_user(user, password=password, token=token, **kwargs)

        if r.status_code == 200:
            self.logged_user = r.json()["user"]

        return r

    def logout_user(self, **kwargs):
        r = super().logout_user(**kwargs)

        if r.status_code == 200:
            self.logged_user = None

        return r

    def setup_user(self, name):
        self.create_user(name, email=f"{name}@example.com", password="password")
        self.validate_email(name, get_email_token(name))
        self.login_user(name)

    @property
    def is_anonymous(self):
        return self.logged_user is None

    @property
    def is_moderator(self):
        return not self.is_anonymous and "moderator" in self.logged_user["roles"]
