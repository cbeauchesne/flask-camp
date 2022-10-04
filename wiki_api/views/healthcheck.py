from wiki_api.decorators import allow

rule = "/healthcheck"


@allow("anonymous")
def get():
    """Ping? pong!"""
    return {"status": "ok"}
