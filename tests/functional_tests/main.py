import requests
from sqlalchemy import create_engine

from tests.utils import ClientInterface


engine = create_engine("postgresql://cms_user:cms_user@localhost:5432/cms")


class Client(ClientInterface):
    domain = "http://localhost:5000"

    def __init__(self, name):
        self.name = name
        self._session = requests.Session()

    def _request(self, method, url, **kwargs):
        r = self._session.request(method, f"{self.domain}{url}", **kwargs, timeout=1)
        print(f"{self} {method.upper()} {url} {r.status_code}")

        return r

    def get(self, url, params=None, headers=None):
        return self._request("get", url, params=params, headers=headers)

    def post(self, url, params=None, json=None, headers=None):
        return self._request("post", url, params=params, headers=headers, json=json)

    def put(self, url, params=None, data=None, json=None, headers=None):
        return self._request("put", url, params=params, headers=headers, json=json, data=data)

    def delete(self, url, params=None, json=None, headers=None):
        return self._request("delete", url, params=params, headers=headers, json=json)

    def __str__(self):
        return self.name


def get_email_token(user_name):
    with engine.connect() as connection:
        rows = connection.execute(f"SELECT email_token FROM user_account WHERE name='{user_name}'")
        token = list(rows)[0][0]
        return token


if __name__ == "__main__":
    anonymous = Client("anonymous")
    admin = Client("admin")

    anonymous.init_database()

    admin.login_user("admin", "password")

    doc = admin.create_document().json()["document"]
    admin.delete_document(doc)

    user = Client("user")
    user.create_user("user")

    user.validate_email("user", get_email_token("user"))

    user.login_user("user")
