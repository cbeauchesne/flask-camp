from wiki_api.decorators import allow

rule = "/healthcheck"


@allow("anonymous", "authenticated", allow_blocked=True)
def get():
    """Ping? pong!"""
    return {"status": "ok"}
