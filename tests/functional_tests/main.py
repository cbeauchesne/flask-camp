import sys

import requests
from sqlalchemy import create_engine

from tests.utils import ClientInterface


engine = create_engine("postgresql://cms_user:cms_user@localhost:5432/cms")


class Client(ClientInterface):
    def __init__(self, name, domain):
        self.name = name
        self.domain = domain
        self._session = requests.Session()

    def _request(self, method, url, expected_status=None, **kwargs):
        r = self._session.request(method, f"{self.domain}{url}", **kwargs, timeout=1)
        print(f"{self} {method.upper()} {url} {r.status_code}")

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

    def __str__(self):
        return self.name


def get_email_token(user_name):
    with engine.connect() as connection:
        rows = connection.execute(f"SELECT email_token FROM user_account WHERE name='{user_name}'")
        token = list(rows)[0][0]
        return token


if __name__ == "__main__":

    anonymous = Client("anonymous", domain="http://localhost:5000")
    anonymous.init_database()

    admin = Client("admin", domain="http://localhost:5000")
    admin.login_user("admin")

    moderator = Client("moderator", domain="http://localhost:5000")
    moderator_id = moderator.create_user("moderator").json()["user"]["id"]
    moderator.validate_email("moderator", get_email_token("moderator"))
    admin.add_user_role(moderator_id, role="moderator", comment="I trust him")
    moderator.login_user("moderator")

    user = Client("user", domain="http://localhost:5000")
    user.create_user("user")
    user.validate_email("user", get_email_token("user"))
    user.login_user("user")

    doc = user.create_document().json()["document"]
    admin.delete_document(doc)

    doc = user.create_document().json()["document"]
    user.protect_document(doc, expected_status=403)
    moderator.protect_document(doc)

    user.modify_document(doc, expected_status=403)
    moderator.modify_document(doc, expected_status=200)

    doc_2 = user.create_document().json()["document"]
    user.modify_document(doc_2, expected_status=200)

    # admin.block_user(user)
