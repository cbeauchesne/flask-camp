# pylint: disable=too-few-public-methods

from flask import request
from flask_login import current_user
from sqlalchemy import Column, String, ForeignKey

from flask_camp import RestApi
from flask_camp.services.database import database
from flask_camp.models import User, BaseModel, Document

from tests.unit_tests.utils import create_test_app


def cooker(document, get_document):
    if document["namespace"] in ("cook-me",):
        document["cooked"] = {}

        # Let's build an app with document. One rule: all documents have (or not) a parent
        # if a document has a parent, it must be present in document["cooked"]["parent"]
        parent_id = document["data"].get("parent_id")
        if parent_id is not None:
            document["cooked"]["parent"] = get_document(parent_id)
        else:
            document["cooked"]["parent"] = None


class DocumentSearch(BaseModel):
    id = Column(ForeignKey(Document.id, ondelete="CASCADE"), index=True, nullable=True, primary_key=True)

    namespace = Column(String(16), index=True)

    @classmethod
    def from_document(cls, document):
        result = cls.get(id=document.id)
        if result is None:
            result = cls(id=document.id)
            database.session.add(result)

        result.namespace = document.namespace

        return result


def before_document_save(document):
    DocumentSearch.from_document(document)


def update_search_query(query):
    namespace = request.args.get("namespace", default=None, type=str)

    if namespace is not None:
        query = query.join(DocumentSearch).where(DocumentSearch.namespace == namespace)

    return query


app = create_test_app()

api = RestApi(
    app=app,
    rate_limit_cost_function=lambda: 0 if current_user.is_admin else 1,
    rate_limits_file="tests/ratelimit_config.json",
    cooker=cooker,
    schemas_directory="tests/unit_tests/schemas",
    document_schemas=["outing.json"],
    user_roles="bot,contributor",
    namespaces=["", "outing", "route", "cook-me", "x"],
    before_document_save=before_document_save,
    update_search_query=update_search_query,
)


class BotModule:
    rule = "/bot"

    @staticmethod
    @api.allow("bot")
    def get():
        """Here is a custom post, only for bots"""
        return {"hello": "world"}


class CustomModule:
    rule = "/custom"

    @staticmethod
    @api.allow("anonymous")
    def get():
        """Here is a custom get"""
        return {"hello": "world"}


class RateLimitedClass:
    rule = "/rate_limited"

    @api.allow("anonymous")
    def get(self):
        """I'm rate limited"""
        return {"hello": "world"}


@app.route("/__testing/500", methods=["GET"])
def testing_500():
    """This function will raise a 500 response"""
    return 1 / 0


@app.route("/__testing/vuln/<int:user_id>", methods=["GET"])
def testing_vuln(user_id):
    """Calling this method without being authentified as user_id mys raise a Forbidden response"""
    return User.get(id=user_id).as_dict(include_personal_data=True)


api.add_modules(app, CustomModule, BotModule, RateLimitedClass())
