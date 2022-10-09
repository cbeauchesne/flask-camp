## Configuration

### Global configuration
Using env vars: see https://flask-limiter.readthedocs.io/en/stable/configuration.html (you need to use the `FLASK_` prefix)

### By method/route configuration

You can provide a json file with limit per route/method using the `rate_limits_file` argument:

```json
{
  "/documents": {
    "GET": "200 per day;50 per hour",
  },
  "/healtcheck": {
    "GET": null
  }
}
```

`null` wil disable any rate limit defined globally with [RATELIMIT_APPLICATION](https://flask-limiter.readthedocs.io/en/stable/configuration.html#RATELIMIT_APPLICATION) or [RATELIMIT_DEFAULT](https://flask-limiter.readthedocs.io/en/stable/configuration.html#RATELIMIT_DEFAULT), which can be something needed for healtcheck

### Define a more custom rate limit 

It can be done by using a cost function : 

```python
def rate_limit_cost_function():
    if current_user.is_admin:
        return 0

    return 1


app, api = RestApi(rate_limit_cost_function=rate_limit_cost_function)
```
