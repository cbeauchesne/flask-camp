from flask_login import current_user

from wiki_api import config as wiki_api_config
from wiki_api import Application


class Config(wiki_api_config.Testing):  # pylint: disable=too-few-public-methods
    RATELIMIT_CONFIGURATION_FILE = "tests/ratelimit_config.json"


def cooker(document, get_document):  # pylint: disable=unused-argument
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

app.register_cooker(cooker)
app.register_schemas("tests/unit_tests/schemas", ["outing.json"])
