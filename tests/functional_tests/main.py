import requests

from tests.utils import ClientInterface


class Client(ClientInterface):
    domain = "http://localhost:5000"

    def __init__(self, name):
        self.name = name
        self._session = requests.Session()

    def _request(self, method, url, **kwargs):
        r = self._session.request(method, f"{self.domain}{url}", **kwargs, timeout=1)
        print(f"{self} {url} {r.status_code}")

    def get(self, url, params=None, headers=None):
        return self._request("get", url, params=params, headers=headers)

    def post(self, url, params=None, json=None, headers=None):
        return self._request("post", url, params=params, headers=headers, json=json)

    def put(self, url, params=None, data=None, json=None, headers=None):
        return self._request("put", url, params=params, headers=headers, json=json, data=data)

    def delete(self, url, params=None, json=None, headers=None):
        return self._request("delete", url, params=params, headers=headers, json=json)

    def init_database(self):
        return self.get("/init_database")

    def __str__(self):
        return self.name


if __name__ == "__main__":
    anonymous = Client("anonymous")
    admin = Client("admin")

    anonymous.init_database()

    admin.login_user("admin", "password")
