from copy import deepcopy


class ClientInterface:
    def get(self, url, params=None, headers=None):
        raise NotImplementedError()

    def post(self, url, params=None, json=None, headers=None):
        raise NotImplementedError()

    def put(self, url, params=None, data=None, json=None, headers=None):
        raise NotImplementedError()

    def delete(self, url, params=None, json=None, headers=None):
        raise NotImplementedError()

    @staticmethod
    def assert_status_code(response, expected_status):
        raise NotImplementedError()

    def create_user(self, name, email, password, expected_status=200):
        r = self.put("/users", json={"name": name, "email": email, "password": password})
        self.assert_status_code(r, expected_status)

        return r

    def login_user(self, user, password="password", expected_status=200):
        name = user if isinstance(user, str) else user.name

        r = self.post("/login", json={"name": name, "password": password})
        self.assert_status_code(r, expected_status)

        return r

    def logout_user(self, expected_status=200):
        r = self.delete("/login")
        self.assert_status_code(r, expected_status)
        return r

    def create_document(self, namespace="", data=None, expected_status=200):
        r = self.put("/documents", json={"document": {"namespace": namespace, "data": data if data else {}}})
        self.assert_status_code(r, expected_status)

        return r

    def get_document(self, document, headers=None, expected_status=200):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.get(f"/document/{document_id}", headers=headers)
        self.assert_status_code(r, expected_status)

        return r

    def get_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.get(f"/version/{version_id}")
        self.assert_status_code(r, expected_status)

        return r

    def modify_document(self, document, comment="default comment", data=None, expected_status=200):
        document_id = document["id"]
        new_version = deepcopy(document)
        new_version["data"] = data if data else {}

        r = self.post(
            f"/document/{document_id}",
            json={"comment": comment, "document": new_version},
        )

        self.assert_status_code(r, expected_status)

        return r

    def hide_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.post(f"/version/{version_id}", json={"comment": "some comment", "hidden": True})
        self.assert_status_code(r, expected_status)

        return r

    def unhide_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.post(f"/version/{version_id}", json={"comment": "some comment", "hidden": False})
        self.assert_status_code(r, expected_status)

        return r

    def protect_document(self, document, expected_status=200):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.put(f"/protect_document/{document_id}", json={"comment": "some comment"})
        self.assert_status_code(r, expected_status)

        return r

    def unprotect_document(self, document, expected_status=200):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.delete(f"/protect_document/{document_id}", json={"comment": "some comment"})
        self.assert_status_code(r, expected_status)

        return r

    def block_user(self, user, expected_status=200):
        r = self.put(f"/block_user/{user.id}", json={"comment": "Some comment"})
        self.assert_status_code(r, expected_status)
        return r

    def unblock_user(self, user, expected_status=200):
        r = self.delete(f"/block_user/{user.id}", json={"comment": "Some comment"})
        self.assert_status_code(r, expected_status)
        return r

    def delete_version(self, version, expected_status=200):
        version_id = version if isinstance(version, int) else version["version_id"]

        r = self.delete(f"/version/{version_id}", json={"comment": "toto"})
        self.assert_status_code(r, expected_status)

        return r

    def delete_document(self, document, expected_status=200):
        document_id = document if isinstance(document, int) else document["id"]

        r = self.delete(f"/document/{document_id}", json={"comment": "comment"})
        self.assert_status_code(r, expected_status)

        return r

    def add_user_tag(self, name, doc, value=None, expected_status=200):
        payload = {"name": name, "document_id": doc["id"]}

        if value is not None:
            payload["value"] = value

        r = self.post("/user_tags", json=payload)

        self.assert_status_code(r, expected_status)

        return r

    def remove_user_tag(self, name, doc, expected_status=200):
        r = self.delete("/user_tags", json={"name": name, "document_id": doc["id"]})
        self.assert_status_code(r, expected_status)

        return r

    def merge_documents(self, document_to_merge, document_destination, expected_status=200):
        payload = {"document_to_merge": document_to_merge["id"], "document_destination": document_destination["id"]}
        r = self.post("/merge", json=payload)

        self.assert_status_code(r, expected_status)

        return r
