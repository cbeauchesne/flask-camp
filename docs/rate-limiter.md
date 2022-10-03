## Configuration

Using env vars: see https://flask-limiter.readthedocs.io/en/stable/configuration.html (you need to use the `FLASK_` prefix)

You can also provide a json file with limit per route/method using the `FLASK_RATELIMIT_CONFIGURATION_FILE`:

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
