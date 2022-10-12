import pytest

from sqlalchemy import Column, ForeignKey, select
from sqlalchemy.orm import relationship
from werkzeug.exceptions import Forbidden

from flask import request
from flask_camp import RestApi, current_api, allow
from flask_camp.models import Document, User, BaseModel
from flask_camp.exceptions import ConfigurationError
from flask_camp.views.content.document import get as get_document_view
from tests.unit_tests.utils import BaseTest


class ProfilePageLink(BaseModel):
    document_id = Column(ForeignKey(Document.id, ondelete="CASCADE"), index=True, nullable=False, unique=True)
    document = relationship(Document, cascade="all,delete")

    user_id = Column(ForeignKey(User.id, ondelete="CASCADE"), index=True, nullable=False, unique=True)
    user = relationship(User, cascade="all,delete")


def before_user_creation(user):
    """
    Two actions:
    1. user must provide a captcha
    2. a document is created, and user id is set to the document's id
    """

    data = request.get_json()
    if "captcha" not in data:
        raise Forbidden()

    user_page = Document.create(
        comment="Creation of user page",
        data={"user_id": user.id},
        author=user,
    )

    current_api.database.session.add(ProfilePageLink(user=user, document=user_page))


class ProfileView:
    rule = "/profile/<string:name>"

    @allow("anonymous")
    def get(self, name):
        query = select(Document.id).join(ProfilePageLink).join(User).where(User.name == name)
        result = current_api.database.session.execute(query)

        return get_document_view(list(result)[0][0])


class Test_Error:
    def test_error(self):
        with pytest.raises(ConfigurationError):
            RestApi(before_user_creation={})


class Test_BeforeUserCreation(BaseTest):
    rest_api_kwargs = {"before_user_creation": before_user_creation}

    def test_main(self):

        self.api.add_modules(self.app, ProfileView())

        self.create_user(expected_status=403)
        user = self.create_user(name="other_user", json={"captcha": 42}, expected_status=200).json["user"]

        documents = self.get_documents(expected_status=200).json["documents"]
        assert "user_id" in documents[0]["data"]
        assert documents[0]["data"]["user_id"] == user["id"]  # check of link
        assert documents[0]["user"]["id"] == user["id"]  # check of page author

        profile = self.get(f"/profile/{user['name']}").json["document"]
        assert profile["data"]["user_id"] == user["id"]
