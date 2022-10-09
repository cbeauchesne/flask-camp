Without any conf, only admins can delete documents. Though, it can be needed to allow user to delete documents. To do so, use this recipe : 

```python
from flask import Flask
from flask_camp import RestApi
from werkzeug.exceptions import Forbidden

def before_document_delete(user, document_as_dict):
    """Stupid test: user cant delete if it's the last editor"""
    if document_as_dict["user"]["id"] == user.id:
        raise Forbidden()


app = Flask(__name__)
RestApi(app=app, user_can_delete=True, before_document_delete=before_document_delete)
```

Your `before_document_delete` function should raise an exception (often a `werkzeug.exceptions.Forbidden`) to prevent a forbidden deletion.