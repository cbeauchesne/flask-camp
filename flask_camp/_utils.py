import json
import typing as t
from http import HTTPStatus

from flask import current_app, request, Response
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


class JsonResponse:
    """Wapper around Flask response object. Usefull to manipulate response as object before really dump it"""

    def __init__(
        self,
        response,
        status: t.Optional[t.Union[int, str, HTTPStatus]] = None,
        headers: t.Optional[
            t.Union[
                t.Mapping[str, t.Union[str, int, t.Iterable[t.Union[str, int]]]],
                t.Iterable[t.Tuple[str, t.Union[str, int]]],
            ]
        ] = None,
        add_etag: bool = False,
    ) -> None:
        self.response = response
        self.status = 200 if status is None else status
        self.headers = {} if headers is None else headers
        self.content_type = "application/json"
        self.add_etag = add_etag

    def build_flask_reponse(self):
        result = Response(
            response=json.dumps(self.response),
            status=self.status,
            headers=self.headers,
            content_type=self.content_type,
        )

        if self.add_etag:
            result.add_etag()
            result.make_conditional(request)

        return result
