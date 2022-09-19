from copy import deepcopy


class BaseTest:
    client = None

    def _assert_status_response(self, r):
        if r.status_code != 304:  # not modified : no body
            assert r.json is not None, r.data
            assert "status" in r.json, r.json

            if r.status_code == 200:
                assert r.json["status"] == "ok", r.json
            else:
                assert r.json["status"] == "error", r.json
                assert "description" in r.json, r.json

    def get(self, *args, **kwargs):
        r = BaseTest.client.get(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def post(self, *args, **kwargs):
        r = BaseTest.client.post(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def put(self, *args, **kwargs):
        r = BaseTest.client.put(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def delete(self, *args, **kwargs):
        r = BaseTest.client.delete(*args, **kwargs)
        self._assert_status_response(r)

        return r

    def login_user(self, user, password="password", expected_status=200):
        name = user if isinstance(user, str) else user.name

        r = self.post("/login", json={"name": name, "password": password})
        assert r.status_code == expected_status, f"Expecting status {expected_status}, got {r.status_code}: {r.json}"

        return r

    def logout_user(self, expected_status=200):
        r = self.delete("/login")
        assert r.status_code == expected_status, r.json
        return r

    # helpers
    def create_document(self, namespace="x", data=None, expected_status=200):
        r = self.put("/documents", json={"document": {"namespace": namespace, "data": data if data else {}}})

        assert r.status_code == expected_status, r.json

        return r

    def get_document(
        self, document, headers=None, expected_status=200, data_should_be_present=True, version_should_be=None
    ):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.get(f"/document/{document_id}", headers=headers)
        assert r.status_code == expected_status, r.json

        if r.status_code == 200:
            if data_should_be_present:
                assert "data" in r.json["document"]
            else:
                assert "data" not in r.json["document"]

            if version_should_be:
                assert r.json["document"]["version_id"] == version_should_be["version_id"]

        return r

    def get_document_version(self, version, expected_status=200, data_should_be_present=True):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.get(f"/document_version/{version_id}")
        assert r.status_code == expected_status

        if r.status_code == 200:
            if data_should_be_present:
                assert "data" in r.json["document"]
            else:
                assert "data" not in r.json["document"]

        return r

    def modify_document(self, document, data=None, comment="empty", expected_status=200):
        document_id = document["id"]
        new_version = deepcopy(document)
        new_version["data"] = data if data else {}

        r = self.post(
            f"/document/{document_id}",
            json={"comment": comment, "document": new_version},
        )

        assert r.status_code == expected_status, r.json

        return r

    def hide_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.post(f"/document_version/{version_id}", json={"comment": "some comment", "hidden": True})
        assert r.status_code == expected_status, r.json

        return r

    def unhide_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.post(f"/document_version/{version_id}", json={"comment": "some comment", "hidden": False})
        assert r.status_code == expected_status, r.json

        return r

    def protect_document(self, document_id, expected_status=200):
        r = self.put(f"/protect_document/{document_id}", json={"comment": "some comment"})
        assert r.status_code == expected_status

        return r

    def unprotect_document(self, document_id, expected_status=200):
        r = self.delete(f"/protect_document/{document_id}", json={"comment": "some comment"})
        assert r.status_code == expected_status

        return r

    def block_user(self, user, expected_status=200):
        r = self.put(f"/block_user/{user.id}", json={"comment": "Some comment"})
        assert r.status_code == expected_status, r.json
        return r

    def unblock_user(self, user, expected_status=200):
        r = self.delete(f"/block_user/{user.id}", json={"comment": "Some comment"})
        assert r.status_code == expected_status, r.json
        return r

    def delete_document_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.delete(f"/document_version/{version_id}", json={"comment": "toto"})
        assert r.status_code == expected_status, r.json

        return r

    def delete_document(self, document, expected_status=200):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.delete(f"/document/{document_id}", json={"comment": "comment"})
        assert r.status_code == expected_status, r.json

        return r

    def add_user_tag(self, name, doc, value=None, expected_status=200):
        payload = {"name": name, "document_id": doc["id"]}

        if value is not None:
            payload["value"] = value

        r = self.post("/user_tags", json=payload)

        assert r.status_code == expected_status, r.json

        return r

    def remove_user_tag(self, name, doc, expected_status=200):
        r = self.delete("/user_tags", json={"name": name, "document_id": doc["id"]})

        assert r.status_code == expected_status, r.json

        return r
