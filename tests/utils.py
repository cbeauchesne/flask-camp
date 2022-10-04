from copy import deepcopy


def _get_user_id(user):
    return user if isinstance(user, int) else user["id"] if isinstance(user, dict) else user.id


class ClientInterface:
    def get(self, url, params=None, headers=None, expected_status=None):
        raise NotImplementedError()

    def post(self, url, params=None, json=None, headers=None, expected_status=None):
        raise NotImplementedError()

    def put(self, url, params=None, data=None, json=None, headers=None, expected_status=None):
        raise NotImplementedError()

    def delete(self, url, params=None, json=None, headers=None, expected_status=None):
        raise NotImplementedError()

    def init_databases(self, expected_status=None):
        return self.get("/init_databases", expected_status=expected_status)

    def create_user(self, name="user", email=None, password="password", expected_status=None):
        email = f"{name}@example.com" if email is None else email

        return self.put(
            "/users", expected_status=expected_status, json={"name": name, "email": email, "password": password}
        )

    def validate_email(self, user, token, expected_status=None):
        name = user if isinstance(user, str) else user["name"] if isinstance(user, dict) else user.name
        return self.post("/validate_email", expected_status=expected_status, json={"name": name, "token": token})

    def resend_email_validation(self, user, expected_status=None):
        name = user if isinstance(user, str) else user["name"] if isinstance(user, dict) else user.name

        return self.get("/validate_email", expected_status=expected_status, params={"name": name})

    def reset_password(self, email, expected_status=None):
        return self.post("/reset_password", json={"email": email}, expected_status=expected_status)

    def login_user(self, user, password="password", token=None, expected_status=None):
        name = user if isinstance(user, str) else user["name"] if isinstance(user, dict) else user.name

        payload = {"name": name}
        if token is not None:
            payload["token"] = token
        else:
            payload["password"] = password

        return self.post("/login", expected_status=expected_status, json=payload)

    def get_current_user(self, expected_status=200):
        return self.get("/current_user", expected_status=expected_status)

    def logout_user(self, expected_status=None):
        return self.delete("/login", expected_status=expected_status)

    def get_user(self, user, expected_status=None):
        user_id = _get_user_id(user)
        return self.get(f"/user/{user_id}", expected_status=expected_status)

    def get_users(self, limit=None, expected_status=None):
        params = {}

        if limit is not None:
            params["limit"] = limit

        return self.get("/users", params=params, expected_status=expected_status)

    def modify_user(
        self,
        user,
        password=None,
        token=None,
        new_password=None,
        email=None,
        ui_preferences=None,
        expected_status=None,
    ):
        user_id = _get_user_id(user)
        payload = {}

        if password is not None:
            payload["password"] = password

        if token is not None:
            payload["token"] = token

        if new_password is not None:
            payload["new_password"] = new_password

        if email is not None:
            payload["email"] = email

        if ui_preferences is not None:
            payload["ui_preferences"] = ui_preferences

        return self.post(f"/user/{user_id}", expected_status=expected_status, json=payload)

    def add_user_role(self, user, role, comment, expected_status=None):
        user_id = _get_user_id(user)

        return self.post(f"/roles/{user_id}", json={"role": role, "comment": comment}, expected_status=expected_status)

    def remove_user_role(self, user, role, comment, expected_status=None):
        user_id = _get_user_id(user)

        return self.delete(
            f"/roles/{user_id}", json={"role": role, "comment": comment}, expected_status=expected_status
        )

    def get_user_roles(self, user, expected_status=None):
        user_id = _get_user_id(user)

        return self.get(f"/roles/{user_id}", expected_status=expected_status)

    def create_document(self, namespace="", data=None, expected_status=None):
        return self.put(
            "/documents",
            expected_status=expected_status,
            json={"comment": "creation", "document": {"namespace": namespace, "data": data if data else {}}},
        )

    def get_documents(
        self, tag_name=None, tag_user=None, tag_value=None, limit=None, offset=None, expected_status=None
    ):
        params = {}

        if tag_name is not None:
            params["tag_name"] = tag_name

        if tag_user is not None:
            params["tag_user_id"] = _get_user_id(tag_user)

        if tag_value is not None:
            params["tag_value"] = tag_value

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        return self.get("/documents", params=params, expected_status=expected_status)

    def get_document(self, document, headers=None, expected_status=None):
        document_id = document if isinstance(document, int) else document["id"]

        return self.get(f"/document/{document_id}", expected_status=expected_status, headers=headers)

    def get_version(self, version, expected_status=None):
        version_id = version if isinstance(version, int) else version["version_id"]

        return self.get(f"/version/{version_id}", expected_status=expected_status)

    def get_versions(self, document=None, limit=None, user=None, tag_name=None, tag_user=None, expected_status=None):
        params = {}

        if document is not None:
            params["document_id"] = document["id"]

        if user is not None:
            params["user_id"] = _get_user_id(user)

        if tag_name is not None:
            params["tag_name"] = tag_name

        if tag_user is not None:
            params["tag_user_id"] = _get_user_id(tag_user)

        if limit is not None:
            params["limit"] = limit

        return self.get("/versions", params=params, expected_status=expected_status)

    def modify_document(self, document, comment="default comment", data=None, params=None, expected_status=None):
        document_id = document["id"]
        new_version = deepcopy(document)
        new_version["data"] = data if data else {}

        return self.post(
            f"/document/{document_id}",
            expected_status=expected_status,
            json={"comment": comment, "document": new_version},
            params=params,
        )

    def hide_version(self, version, expected_status=None):
        version_id = version if isinstance(version, int) else version["version_id"]

        return self.post(
            f"/version/{version_id}", expected_status=expected_status, json={"comment": "some comment", "hidden": True}
        )

    def unhide_version(self, version, expected_status=None):
        version_id = version if isinstance(version, int) else version["version_id"]

        return self.post(
            f"/version/{version_id}", expected_status=expected_status, json={"comment": "some comment", "hidden": False}
        )

    def protect_document(self, document, expected_status=None):
        document_id = document if isinstance(document, int) else document["id"]

        return self.post(
            f"/protect_document/{document_id}",
            json={"comment": "some comment", "protected": True},
            expected_status=expected_status,
        )

    def unprotect_document(self, document, expected_status=None):
        document_id = document if isinstance(document, int) else document["id"]

        return self.post(
            f"/protect_document/{document_id}",
            json={"comment": "some comment", "protected": False},
            expected_status=expected_status,
        )

    def block_user(self, user, comment="Some comment", expected_status=None):
        user_id = _get_user_id(user)
        return self.post(
            f"/block_user/{user_id}", expected_status=expected_status, json={"comment": comment, "blocked": True}
        )

    def unblock_user(self, user, comment="Some comment", expected_status=None):
        user_id = _get_user_id(user)
        return self.post(
            f"/block_user/{user_id}", expected_status=expected_status, json={"comment": comment, "blocked": False}
        )

    def delete_version(self, version, expected_status=None):
        version_id = version if isinstance(version, int) else version["version_id"]

        return self.delete(f"/version/{version_id}", expected_status=expected_status, json={"comment": "toto"})

    def delete_document(self, document, expected_status=None):
        document_id = document if isinstance(document, int) else document["id"]

        return self.delete(f"/document/{document_id}", expected_status=expected_status, json={"comment": "comment"})

    def get_user_tags(self, user=None, document=None, name=None, limit=None, expected_status=None):
        params = {}

        if document is not None:
            params["document_id"] = document["id"]

        if user is not None:
            params["user_id"] = _get_user_id(user)

        if name is not None:
            params["name"] = name

        if limit is not None:
            params["limit"] = limit

        return self.get("/user_tags", params=params, expected_status=expected_status)

    def add_user_tag(self, name, doc, value=None, expected_status=None):
        payload = {"name": name, "document_id": doc["id"]}

        if value is not None:
            payload["value"] = value

        return self.post("/user_tags", expected_status=expected_status, json=payload)

    def remove_user_tag(self, name, document, expected_status=None):
        return self.delete(
            "/user_tags", expected_status=expected_status, json={"name": name, "document_id": document["id"]}
        )

    def merge_documents(self, document_to_merge, document_destination, comment=None, expected_status=None):
        payload = {"document_to_merge": document_to_merge["id"], "document_destination": document_destination["id"]}

        if comment:
            payload["comment"] = comment

        return self.post("/merge", expected_status=expected_status, json=payload)

    def get_logs(self, limit=None, expected_status=None):
        params = {}

        if limit is not None:
            params["limit"] = limit

        return self.get("/logs", params=params, expected_status=expected_status)
