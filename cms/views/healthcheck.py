from cms.limiter import limiter
from cms.decorators import allow

rule = "/healthcheck"


@limiter.limit("1/minute")
@allow("anonymous")
def get():
    return {"status": "ok"}
