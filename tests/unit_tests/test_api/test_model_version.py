import pytest
from werkzeug.exceptions import BadRequest

from flask_camp.models import DocumentVersion
from tests.unit_tests.utils import BaseTest


def test_data():
    version = DocumentVersion(data=None)
    assert version._data == "null"

    version.data = {"hello": "world"}
    assert version._data == '{"hello": "world"}'


class Test_Document(BaseTest):
    def test_do_delete_all_versions(self, user):
        self.login_user(user)

        v1 = self.create_document().json["document"]

        with self.app.app_context():
            v1 = DocumentVersion.get(id=v1["version_id"])
            v1.document.last_version_id = None
            self.api.database.session.delete(v1)
            self.api.database.session.commit()

            with pytest.raises(BadRequest):
                v1.document.update_last_version_id()

    def test_do_hide_last_versions(self, user):
        self.login_user(user)

        v1 = self.create_document().json["document"]

        with self.app.app_context():
            v1 = DocumentVersion.get(id=v1["version_id"])
            v1.hidden = True
            self.api.database.session.commit()

            with pytest.raises(BadRequest):
                v1.document.update_last_version_id()
