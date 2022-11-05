You can add custom rules to your app using any regular flask method, for instance : 

```python
@app.route("/my_custom_route", methods=["GET"])
def hello():
    return {"hello": "world"}
```

If you returns a dict, Flask transforms it as a JSON response. Any other response will be treated like a normal Flask app.

Though, you can benifit of some feature of flask camp if you use the `FlaskCamp.add_views()` method:

- you can define rate limits on your URL rules as any other rule
- it requires to use `@allow` on all your method, following the golden rule "_security: everything is forbidden, except if it's allowed_".

A "view" is an object (a module, a class, or a class instance) with one or more of those attributes (`get`, `post`, `put`, `delete`) : 


*my_custom_route.py*

```python
""" Example of module view """
from flask_camp import allow


rule = "/my_custom_route"

@allow("anonymous")
def get():
    return {"hello": "world"}

@allow("anonymous")
def post():
    return {"hello": "world"}
```


*module_with_class.py*
```python
""" Example of class instance view """
from flask_camp import allow


class CustomRoute:
    rule = "/my_custom_route2"

    @allow("anonymous")
    def get(self):
        return {"hello": "world"}

    @allow("anonymous")
    def post(self):
    return {"hello": "world"}
```

*app.py*
```python
from flask import Flask
from flask_camp import RestApi

import my_custom_route
from module_with_class import CustomRoute


app = Flask(__name__)
api = RestApi(app)
api.add_views(app, my_custom_route, CustomRoute())
```
