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
        "before_update_document": hooks.before_update_document,
        "before_merge_documents": hooks.before_merge_documents,
        "after_merge_documents": hooks.after_merge_documents,
        "before_delete_document": hooks.before_delete_document,
        "after_delete_document": hooks.after_delete_document,
    }

    def setup_method(self):
        super().setup_method()
        hooks.reset_mock()

    def test_main(self, moderator, admin):

        self.login_user(moderator)

        doc1 = self.create_document().json["document"]
        self.assert_call(hooks.before_create_document, document=Document)
        self.assert_call(hooks.after_create_document, response=JsonResponse)
        hooks.reset_mock()

        doc2 = self.create_document().json["document"]
        doc3 = self.create_document().json["document"]
        hooks.reset_mock()

        self.get_document(doc1)
        self.assert_call(hooks.after_get_document, response=JsonResponse)
        hooks.reset_mock()

        self.get_documents()
        self.assert_call(hooks.after_get_documents, response=JsonResponse)
        hooks.reset_mock()

        self.merge_documents(doc1, doc2)
        self.assert_call(hooks.before_merge_documents, document_to_merge=Document, document_destination=Document)
        self.assert_call(hooks.after_merge_documents, response=JsonResponse)
        assert hooks.before_update_document.call_count == 0
        hooks.reset_mock()

        self.merge_documents(doc3, doc2)
        self.assert_call(hooks.before_merge_documents, document_to_merge=Document, document_destination=Document)
        self.assert_call(
            hooks.before_update_document, document=Document, old_version=DocumentVersion, new_version=DocumentVersion
        )
        self.assert_call(hooks.after_merge_documents, response=JsonResponse)
        hooks.reset_mock()

        # todo test hide, with lot of possibility

        self.login_user(admin)
        self.delete_document(doc1)
        self.assert_call(hooks.before_delete_document, document=Document)
        self.assert_call(hooks.after_delete_document, response=JsonResponse)

    def assert_call(self, function, **kwargs):
        assert function.call_count == 1
        function_kwargs = function.call_args_list[0].kwargs
        assert len(function.call_args_list[0].args) == 0  # always kwargs
        assert len(function_kwargs) == len(kwargs)

        for key, klass in kwargs.items():
            assert key in function_kwargs
            assert isinstance(function_kwargs[key], klass)

        function.reset_mock()
