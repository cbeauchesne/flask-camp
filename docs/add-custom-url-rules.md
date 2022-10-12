You may want to add your custom URL rules. 


## Using regular flask 
As you're using a normal Flask app, any usual method works :

```python
@app.route("/my_custom_route", methods=["GET"])
def hello():
    return {"hello": "world"}
```

If you returns a dict, Flask transforms it as a JSON response. Any other response will be treated like a normal Flask app

## Using `add_modules` method

Though, a convenient way to declare REST API is implemented using the `add_modules` method. Simply declare a class or a module with a `rule` attribute, and one or more method in `get`, `post`, `put`, `delete`, it will be mapped to the relevant method/endpoints:

### Define your routes as a module

*my_custom_route.py*

```python
from flask_camp import allow


rule = "/my_custom_route"

@allow("anonymous")
def get():
    return {"hello": "world"}

@allow("anonymous")
def post():
    return {"hello": "world"}
```

### Define your routes as a class instance

*module_with_class.py*
```python

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

----

Those three routes can be imported with the `add_modules` method. Please note that `CustomRoute` should be an instance of the class :

```python
from flask import Flask
from flask_camp import RestApi

import my_custom_route
from module_with_class import CustomRoute


app = Flask(__name__)
api = RestApi(app)
api.add_modules(app, my_custom_route, CustomRoute())
```

The convinient part is :

- you can define rate limits on your URL rules as any other rule
- it requires to use `@allow` on all your method, following the golden rule "_security: everything is forbidden, except if it's allowed_".
