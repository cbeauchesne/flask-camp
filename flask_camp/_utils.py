from flask import current_app
from werkzeug.exceptions import NotFound
from werkzeug.local import LocalProxy


current_api = LocalProxy(lambda: current_app.extensions["flask-camp"])
get_cooked_document = LocalProxy(lambda: current_api.get_cooked_document)
get_document = LocalProxy(lambda: current_api.get_document)
cook = LocalProxy(lambda: current_api.cook)


class GetDocument:  # pylint: disable=too-few-public-methods
    """This class is a callable the memorize wich arguments has been called
    It's used for the cooker
    """

    def __init__(self, original_get_document):
        self.loaded_document_ids = set()
        self.original_get_document = original_get_document

    def __call__(self, document_id):
        self.loaded_document_ids.add(document_id)
        try:
            return self.original_get_document(document_id)
        except NotFound:
            # it's a possible outcome, if the document has been deleted
            # In that situation, returns None
            return None
