Two roles exists by default : 

* `admin`: can delete versions/documents, and grant/remove roles
* `moderator`: can hide/unhide versions, protect/unprotect documents, merge documents and block/unblock users

Two other technical roles also exists :

* `anonymous` : for non-logged users
* `authenticated` : for logged users

Except for `anonymous` users, any user can have as many role as needed. Though, to define custom roles, you need to use the `FLASK_POSSIBLE_USER_ROLES` en var, or the `POSSIBLE_USER_ROLES` config key.

Then, you'll be able to define any authorization using the `@allow` decorator:

```python
# my_custom_route.py

from wiki_api.services.security import allow


rule = "/my_custom_route"

@allow("bot")
def get():
    return {"hello": "world"}
```
