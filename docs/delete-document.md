Without any conf, only admins can delete documents. Though, it can be needed to allow user to delete documents. To do so, you cam simply add a new endpoint :  

```python
from flask import Flask
from flask_camp import RestApi, current_api
from werkzeug.exceptions import Forbidden


class CustomDelete():
    rule = "/custom_delete/<int:document_id>"

    @allow("authenticated")
    def delete(self, document_id):
        """Delete a document"""

        document = Document.get(id=document_id)
        
        if not logic_to_allow_deletion(document):
            raise Forbidden()

        current_api.database.session.delete(document)

        current_api.add_log("delete_document", document=document, comment="Custom delete")
        current_api.database.session.commit()

        document.clear_memory_cache()

        return {"status": "ok"}


app = Flask(__name__)
api = RestApi(app=app)
api.add_modules(app, CustomDelete())
```
