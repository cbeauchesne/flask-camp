Two roles exists by default : 

* `admin`: can delete versions/documents, and grant/remove roles
* `moderator`: can hide/unhide versions, protect/unprotect documents, merge documents and block/unblock users

Two other technical roles also exists :

* `anonymous` : for non-logged users
* `authenticated` : for logged users

Except for `anonymous` users, any user can have as many role as needed. Though, to define custom roles, you need to use the `user_roles` argument.

Then, you'll be able to define any authorization using the `@allow` decorator:

*app.py*

```python
from flask import Flask
from flask_camp import RestApi
import custom_route.py

app = Flask()
api = RestApi(app, user_roles="bot,contributor")
api.add_module(app, custom_route)
```

*custom_route.py*

```python
from flask_camp.services.security import allow

rule = "/my_custom_route"

@allow("bot")
def get():
    return {"hello": "world"}
```
