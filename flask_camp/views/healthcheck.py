from flask_camp.services.security import allow

rule = "/healthcheck"


@allow("anonymous", "authenticated", allow_blocked=True)
def get():
    """Ping? pong!"""
    return {"status": "ok"}
