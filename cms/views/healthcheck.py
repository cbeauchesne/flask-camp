from cms.decorators import allow

rule = "/healthcheck"


@allow("anonymous")
def get():
    """Ping? pong!"""
    return {"status": "ok"}
