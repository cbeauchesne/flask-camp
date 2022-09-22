from tests.utils import ClientInterface


class BaseTest(ClientInterface):
    client = None

    def get(self, url, params=None, headers=None):
        r = BaseTest.client.get(url, query_string=params, headers=headers)
        self._assert_status_response(r)

        return r

    def post(self, url, params=None, json=None, headers=None):
        r = BaseTest.client.post(url, query_string=params, json=json, headers=headers)
        self._assert_status_response(r)

        return r

    def put(self, url, params=None, data=None, json=None, headers=None):
        r = BaseTest.client.put(url, query_string=params, data=data, json=json, headers=headers)
        self._assert_status_response(r)

        return r

    def delete(self, url, params=None, json=None, headers=None):
        r = BaseTest.client.delete(url, query_string=params, json=json, headers=headers)
        self._assert_status_response(r)

        return r

    @staticmethod
    def assert_status_code(response, expected_status):
        assert (
            response.status_code == expected_status
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

    def get_document(
        self, document, headers=None, expected_status=200, data_should_be_present=True, version_should_be=None
    ):
        r = super().get_document(document, headers=headers, expected_status=expected_status)

        if r.status_code == 200:
            if data_should_be_present:
                assert "data" in r.json["document"]
            else:
                assert "data" not in r.json["document"]

            if version_should_be:
                assert r.json["document"]["version_id"] == version_should_be["version_id"]

        return r

    def get_version(self, version, expected_status=200, data_should_be_present=True):
        r = super().get_version(version, expected_status=expected_status)

        if r.status_code == 200:
            if data_should_be_present:
                assert "data" in r.json["document"]
            else:
                assert "data" not in r.json["document"]

        return r
