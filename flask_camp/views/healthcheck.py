from flask_camp._services._security import allow

rule = "/healthcheck"


@allow("anonymous", "authenticated", allow_blocked=True)
def get():
    """Ping? pong!"""
    return {"status": "ok"}
