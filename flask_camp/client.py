from copy import deepcopy


class ClientInterface:
    @staticmethod
    def _get_user_id(user):
        return user if isinstance(user, int) else user["id"] if isinstance(user, dict) else user.id

    @staticmethod
    def _get_document_id(document):
        return document if isinstance(document, int) else document["id"] if isinstance(document, dict) else document.id

    def get(self, url, **kwargs):
        raise NotImplementedError()

    def post(self, url, **kwargs):
        raise NotImplementedError()

    def put(self, url, **kwargs):
        raise NotImplementedError()

    def delete(self, url, **kwargs):
        raise NotImplementedError()

    ###########################################################################################

    def create_user(self, name, email, password, ui_preferences=None, **kwargs):
        json = {"name": name, "email": email, "password": password, "ui_preferences": ui_preferences}
        json = json | kwargs.pop("json", {})

        return self.post("/users", json=json, **kwargs)

    def validate_email(self, user, token, **kwargs):
        name = user if isinstance(user, str) else user["name"] if isinstance(user, dict) else user.name
        return self.put("/user/validate_email", json={"name": name, "token": token}, **kwargs)

    def resend_email_validation(self, user, **kwargs):
        name = user if isinstance(user, str) else user["name"] if isinstance(user, dict) else user.name
        return self.get("/user/validate_email", params={"name": name}, **kwargs)

    def reset_password(self, email, **kwargs):
        return self.put("/user/reset_password", json={"email": email}, **kwargs)

    def login_user(self, user, password=None, token=None, **kwargs):
        name = user if isinstance(user, str) else user["name"] if isinstance(user, dict) else user.name

        payload = {"name_or_email": name}
        if token is not None:
            payload["token"] = token
        else:
            payload["password"] = password

        return self.put("/user/login", json=payload | kwargs.pop("json", {}), **kwargs)

    def get_current_user(self, **kwargs):
        return self.get("/user/current", **kwargs)

    def logout_user(self, **kwargs):
        return self.delete("/user/login", **kwargs)

    def get_user(self, user, **kwargs):
        user_id = self._get_user_id(user)
        return self.get(f"/user/{user_id}", **kwargs)

    def get_users(self, limit=None, **kwargs):
        params = {}

        if limit is not None:
            params["limit"] = limit

        return self.get("/users", params=params | kwargs.pop("params", {}), **kwargs)

    def modify_user(
        self,
        user,
        name=None,
        password=None,
        token=None,
        new_password=None,
        email=None,
        roles=None,
        blocked=None,
        ui_preferences=None,
        comment="default comment",
        **kwargs,
    ):
        user_id = self._get_user_id(user)
        json = {"user": {}, "comment": comment} | kwargs.pop("json", {})

        if name is not None:
            json["user"]["name"] = name

        if password is not None:
            json["user"]["password"] = password

        if token is not None:
            json["user"]["token"] = token

        if new_password is not None:
            json["user"]["new_password"] = new_password

        if email is not None:
            json["user"]["email"] = email

        if roles is not None:
            json["user"]["roles"] = roles

        if blocked is not None:
            json["user"]["blocked"] = blocked

        if ui_preferences is not None:
            json["user"]["ui_preferences"] = ui_preferences

        return self.put(f"/user/{user_id}", json=json, **kwargs)

    def rename_user(self, user, name, comment, **kwargs):
        return self.modify_user(user, name=name, comment=comment, **kwargs)

    def create_document(self, data, comment, **kwargs):
        return self.post(
            "/documents",
            json={"comment": comment, "document": {"data": data}} | kwargs.pop("json", {}),
            **kwargs,
        )

    def get_documents(
        self,
        limit=None,
        offset=None,
        tag_name=None,
        tag_user=None,
        tag_value=None,
        **kwargs,
    ):
        params = {}

        if tag_name is not None:
            params["tag_name"] = tag_name

        if tag_user is not None:
            params["tag_user_id"] = self._get_user_id(tag_user)

        if tag_value is not None:
            params["tag_value"] = tag_value

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        return self.get("/documents", params=params | kwargs.pop("params", {}), **kwargs)

    def get_document(self, document, **kwargs):
        document_id = document if isinstance(document, int) else document["id"]
        return self.get(f"/document/{document_id}", **kwargs)

    def get_version(self, version, **kwargs):
        version_id = version if isinstance(version, int) else version["version_id"]
        return self.get(f"/document/version{version_id}", **kwargs)

    def get_versions(self, document=None, limit=None, user=None, tag_name=None, tag_user=None, **kwargs):
        params = {}

        if document is not None:
            params["document_id"] = document["id"]

        if user is not None:
            params["user_id"] = self._get_user_id(user)

        if tag_name is not None:
            params["tag_name"] = tag_name

        if tag_user is not None:
            params["tag_user_id"] = self._get_user_id(tag_user)

        if limit is not None:
            params["limit"] = limit

        return self.get("/documents/versions", params=params | kwargs.pop("params", {}), **kwargs)

    def modify_document(self, document, comment, data, **kwargs):
        document_id = self._get_document_id(document)
        new_version = deepcopy(document)
        new_version["data"] = data

        return self.post(
            f"/document/{document_id}",
            json={"comment": comment, "document": new_version} | kwargs.pop("json", {}),
            **kwargs,
        )

    def hide_version(self, version, comment, **kwargs):
        version_id = version if isinstance(version, int) else version["version_id"]
        return self.put(
            f"/document/version{version_id}",
            json={"comment": comment, "version": {"hidden": True}} | kwargs.pop("json", {}),
            **kwargs,
        )

    def unhide_version(self, version, comment, **kwargs):
        version_id = version if isinstance(version, int) else version["version_id"]
        return self.put(
            f"/document/version{version_id}",
            json={"comment": comment, "version": {"hidden": False}} | kwargs.pop("json", {}),
            **kwargs,
        )

    def protect_document(self, document, comment, **kwargs):
        document_id = document if isinstance(document, int) else document["id"]
        return self.put(
            f"/document/{document_id}",
            json={"comment": comment, "document": {"protected": True}},
            **kwargs,
        )

    def unprotect_document(self, document, comment, **kwargs):
        document_id = document if isinstance(document, int) else document["id"]

        return self.put(
            f"/document/{document_id}",
            json={"comment": comment, "document": {"protected": False}} | kwargs.pop("json", {}),
            **kwargs,
        )

    def block_user(self, user, comment, **kwargs):
        return self.modify_user(user, blocked=True, comment=comment, **kwargs)

    def unblock_user(self, user, comment, **kwargs):
        return self.modify_user(user, blocked=False, comment=comment, **kwargs)

    def delete_version(self, version, comment, **kwargs):
        version_id = version if isinstance(version, int) else version["version_id"]
        return self.delete(
            f"/document/version{version_id}", json={"comment": comment} | kwargs.pop("json", {}), **kwargs
        )

    def delete_document(self, document, comment, **kwargs):
        document_id = document if isinstance(document, int) else document["id"]
        return self.delete(f"/document/{document_id}", json={"comment": comment} | kwargs.pop("json", {}), **kwargs)

    def get_user_tags(self, limit=None, offset=None, user=None, document=None, name=None, **kwargs):
        params = {}

        if document is not None:
            params["document_id"] = self._get_document_id(document)

        if user is not None:
            params["user_id"] = self._get_user_id(user)

        if name is not None:
            params["name"] = name

        if limit is not None:
            params["limit"] = limit

        if limit is not None:
            params["offset"] = offset

        return self.get("/user_tags", params=params | kwargs.pop("params", {}), **kwargs)

    def add_user_tag(self, name, document, value=None, **kwargs):
        json = {"name": name, "document_id": self._get_document_id(document)}

        if value is not None:
            json["value"] = value

        return self.post("/user_tags", json=json | kwargs.pop("json", {}), **kwargs)

    def remove_user_tag(self, name, document, **kwargs):
        return self.delete(
            "/user_tags",
            json={
                "name": name,
                "document_id": self._get_document_id(document),
            }
            | kwargs.pop("json", {}),
            **kwargs,
        )

    def merge_documents(self, document_to_merge, document_destination, comment, **kwargs):
        json = {
            "document_to_merge": document_to_merge["id"],
            "document_destination": document_destination["id"],
            "comment": comment,
        } | kwargs.pop("params", {})

        return self.put("/documents/merge", json=json, **kwargs)

    def get_logs(self, limit=None, **kwargs):
        params = {}

        if limit is not None:
            params["limit"] = limit

        return self.get("/logs", params=params | kwargs.pop("params", {}), **kwargs)
