# pylint: disable=too-few-public-methods

from flask_login import current_user

from flask_camp import Application, config as flask_camp_config
from flask_camp.models.user import User


class Config(flask_camp_config.Testing):
    RATELIMIT_CONFIGURATION_FILE = "tests/ratelimit_config.json"
    POSSIBLE_USER_ROLES = "bot,contributor"


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


app = Application(
    config_object=Config,
    rate_limit_cost_function=lambda: 0 if current_user.is_admin else 1,
)


class BotModule:
    rule = "/bot"

    @staticmethod
    @app.allow("bot")
    def get():
        """Here is a custom post, only for bots"""
        return {"hello": "world"}


class CustomModule:
    rule = "/custom"

    @staticmethod
    @app.allow("anonymous")
    def get():
        """Here is a custom get"""
        return {"hello": "world"}


@app.route("/__testing/500", methods=["GET"])
def testing_500():
    """This function will raise a 500 response"""
    return 1 / 0


@app.route("/__testing/vuln/<int:user_id>", methods=["GET"])
def testing_vuln(user_id):
    """Calling this method without being authentified as user_id mys raise a Forbidden response"""
    return User.get(id=user_id).as_dict(include_personal_data=True)


app.add_modules(CustomModule, BotModule)
app.register_cooker(cooker)
app.register_schemas("tests/unit_tests/schemas", ["outing.json"])
