## Goals

1. each user should have a profile page
2. you can get an user profile page with `/profile/<name>`

## How-to

Add a `before_user_creation` hook like this :

```python
from flask import request
from flask_camp import RestApi
from flask_camp.models import User, Document
from sqlalchemy import Column, ForeignKey, select


# Make the link between the user and the profile page in DB
class ProfilePageLink(BaseModel):
    document_id = Column(ForeignKey(Document.id, ondelete="CASCADE"), index=True, nullable=False, unique=True)
    document = relationship(Document, cascade="all,delete")

    user_id = Column(ForeignKey(User.id, ondelete="CASCADE"), index=True, nullable=False, unique=True)
    user = relationship(User, cascade="all,delete")


# add a hook theat will create the page and the link
def before_user_creation(user):

    # create the profile page. This function adds the page in the session
    user_page = Document.create(comment="Creation of user page", data="Hello!", author=user)

    # create the link
    current_api.database.session.add(ProfilePageLink(user=user, document=user_page))


# expose an entry point that returns the profile page given the user name
class ProfileView:
    rule = "/profile/<string:name>"

    @allow("anonymous")
    def get(self, name):
        """ Returns profile page of an user """
        query = select(Document.id).join(ProfilePageLink).join(User).where(User.name == name)
        result = current_api.database.session.execute(query)

        return get_document_view(list(result)[0][0])

app = Flask(__name__)
api = RestApi(app=app, before_user_creation=before_user_creation)

api.add_modules(app, ProfileView())
```
