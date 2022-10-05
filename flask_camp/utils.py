from werkzeug.exceptions import NotFound


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
