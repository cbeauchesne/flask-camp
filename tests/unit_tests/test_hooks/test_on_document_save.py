from contextlib import contextmanager

from tests.unit_tests.utils import BaseTest

NOT_YET_KNOWN = {}


class Hooks:

    calls = []

    @staticmethod
    @contextmanager
    def expect_single_call(document, old_version, new_version):
        Hooks.calls = [
            (document, old_version, new_version),
        ]

        yield

        assert len(Hooks.calls) == 0, "I was expecting more calls"

    @staticmethod
    @contextmanager
    def expect(calls):
        Hooks.calls = calls

        yield

        assert len(Hooks.calls) == 0, "I was expecting more calls"

    @staticmethod
    def on_document_save(document, old_version, new_version):

        if len(Hooks.calls) == 0:
            raise Exception("I should not have been called")

        expected_document, expected_old_version, expected_new_version = Hooks.calls.pop(0)

        assert document is not None

        if new_version is not None:
            assert new_version is document.last_version

        if new_version is not None and old_version is not None:
            assert new_version.id != old_version.id

        if expected_document is not None:
            assert document.id == expected_document["id"]

        if expected_old_version is not None:
            assert old_version is not None
            assert old_version.id == expected_old_version["version_id"]
        else:
            assert old_version is None

        if expected_new_version is NOT_YET_KNOWN:
            assert new_version is not None
        elif expected_new_version is not None:
            assert new_version is not None
            assert new_version.id == expected_new_version["version_id"]
        else:
            assert new_version is None


class Test_UserCreation(BaseTest):
    rest_api_kwargs = {"on_document_save": Hooks.on_document_save}

    def test_regular(self, moderator, admin):
        self.login_user(moderator)

        with Hooks.expect_single_call(document=None, old_version=None, new_version=NOT_YET_KNOWN):
            doc_v1 = self.create_document().json["document"]

        with Hooks.expect_single_call(document=doc_v1, old_version=doc_v1, new_version=NOT_YET_KNOWN):
            doc_v2 = self.modify_document(doc_v1, data=42).json["document"]

        # on_document_save is not called
        self.protect_document(doc_v1)
        self.unprotect_document(doc_v1)

        # hide not the last version => no call
        self.hide_version(doc_v1)
        self.unhide_version(doc_v1)

        with Hooks.expect_single_call(document=doc_v1, old_version=doc_v2, new_version=doc_v1):
            self.hide_version(doc_v2)

        with Hooks.expect_single_call(document=doc_v1, old_version=doc_v1, new_version=doc_v2):
            self.unhide_version(doc_v2)

        with Hooks.expect_single_call(document=doc_v1, old_version=doc_v2, new_version=NOT_YET_KNOWN):
            doc_v3 = self.modify_document(doc_v2, data=43).json["document"]

        self.login_user(admin)

        # not the last version, no call
        self.delete_version(doc_v2)

        with Hooks.expect_single_call(document=doc_v1, old_version=doc_v3, new_version=doc_v1):
            self.delete_version(doc_v3)

    def test_merge(self, moderator):
        self.login_user(moderator)

        with Hooks.expect_single_call(document=None, old_version=None, new_version=NOT_YET_KNOWN):
            doc_1 = self.create_document().json["document"]

        with Hooks.expect_single_call(document=None, old_version=None, new_version=NOT_YET_KNOWN):
            doc_2 = self.create_document().json["document"]

        with Hooks.expect_single_call(document=None, old_version=None, new_version=NOT_YET_KNOWN):
            doc_3 = self.create_document().json["document"]

        with Hooks.expect_single_call(document=doc_1, old_version=doc_1, new_version=None):
            self.merge_documents(doc_1, doc_2)

        with Hooks.expect(
            [
                (doc_2, doc_2, doc_3),  # destination, doc_3 is more recent
                (doc_3, doc_3, None),  # merged document
            ]
        ):
            self.merge_documents(doc_3, doc_2)
