from cms.decorators import allow_anonymous

rule = "/healthcheck"


@allow_anonymous
def get():
    return {"status": "ok"}
