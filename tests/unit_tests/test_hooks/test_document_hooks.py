from unittest.mock import MagicMock
from flask_camp.utils import JsonResponse
from flask_camp.models import Document, DocumentVersion
from tests.unit_tests.utils import BaseTest

hooks = MagicMock()


class Test_Hooks(BaseTest):
    rest_api_kwargs = {
        "before_create_document": hooks.before_create_document,
        "after_create_document": hooks.after_create_document,
        "after_get_document": hooks.after_get_document,
        "after_get_documents": hooks.after_get_documents,
    }

    def setup_method(self):
        super().setup_method()
        hooks.reset_mock()

    def test_main(self, user):

        self.login_user(user)

        doc = self.create_document().json["document"]
        self.assert_call(hooks.before_create_document, document=Document, version=DocumentVersion)
        self.assert_call(hooks.after_create_document, response=JsonResponse)
        hooks.reset_mock()

        self.get_document(doc)
        self.assert_call(hooks.after_get_document, response=JsonResponse)
        hooks.reset_mock()

        self.get_documents()
        self.assert_call(hooks.after_get_documents, response=JsonResponse)
        hooks.reset_mock()

    def assert_call(self, function, **kwargs):
        assert function.call_count == 1
        function_kwargs = function.call_args_list[0].kwargs
        assert len(function.call_args_list[0].args) == 0  # always kwargs
        assert len(function_kwargs) == len(kwargs)

        for key, klass in kwargs.items():
            assert key in function_kwargs
            assert isinstance(function_kwargs[key], klass)

        function.reset_mock()
