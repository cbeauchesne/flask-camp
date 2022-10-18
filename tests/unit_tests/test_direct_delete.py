from flask_camp.models import Document, DocumentVersion, User
from tests.unit_tests.utils import BaseTest


class Test_DirectDelete(BaseTest):
    def test_main(self, user):
        with self.app.app_context():
            doc = Document.create("", {}, User.get(user.id))
            assert DocumentVersion.query.count() == 1

            self.api.database.session.commit()

            doc = Document.get(doc.id)
            self.api.database.session.delete(doc)
            self.api.database.session.commit()

            assert DocumentVersion.query.count() == 0

            doc = Document.create("", {}, User.get(user.id))
            assert DocumentVersion.query.count() == 1

            Document.query.filter(Document.id.in_([doc.id])).update({"last_version_id": None})
            self.api.database.session.query(DocumentVersion).filter(DocumentVersion.document_id.in_([doc.id])).delete(
                synchronize_session=False
            )
            self.api.database.session.query(Document).filter(Document.id.in_([doc.id])).delete(
                synchronize_session=False
            )

            self.api.database.session.commit()

            assert Document.query.count() == 0
            assert DocumentVersion.query.count() == 0
