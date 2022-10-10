from flask_login import current_user

from flask_camp._services._security import allow

rule = "/current_user"


@allow("authenticated", allow_blocked=True)
def get():
    """Get the current authenticated user"""
    return {"status": "ok", "user": current_user.as_dict(include_personal_data=True)}
