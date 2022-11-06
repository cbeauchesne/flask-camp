from unittest.mock import MagicMock
from flask_camp._utils import JsonResponse
from tests.unit_tests.utils import BaseTest

hooks = MagicMock()


class Test_AfterGetDocument(BaseTest):
    rest_api_kwargs = {
        "after_get_document": hooks.after_get_document,
    }

    def test_main(self, user):
        self.login_user(user)

        doc = self.create_document().json["document"]
        assert not hooks.after_get_document.called

        self.get_document(doc)
        assert hooks.after_get_document.call_count == 1
        args = hooks.after_get_document.call_args_list[0].args
        kwargs = hooks.after_get_document.call_args_list[0].kwargs
        assert len(args) == 0
        assert len(kwargs) == 1
        assert isinstance(kwargs["response"], JsonResponse)
