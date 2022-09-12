from cms.decorators import allow

rule = "/healthcheck"


@allow("anonymous")
def get():
    return {"status": "ok"}
