## Goals

1. each user should have a profile page
2. user id should be equals to it's own profile page's id

## How-to

Add a `before_user_creation` hook like this : 

``` python
from flask import request
from flask_camp import RestApi
from flask_camp.models import User, Document

def before_user_creation(user):

    # get the system user, as all docs must have an author, and user is not yet created 
    admin_user = User.get(id=1)

    # create the page. This function adds the page in the session
    user_page = Document.create(
        namespace="profile",
        comment="Automatic creation of user page",
        data=None,
        author=admin_user,
    )

    # force user.id to be equal to user_page.id
    user.id = user_page.id

app = Flask(__name__)
api = RestApi(app=app, before_user_creation=before_user_creation)
```
