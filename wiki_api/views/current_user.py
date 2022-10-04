from flask_login import current_user

from wiki_api.decorators import allow

rule = "/current_user"


@allow("blocked")
def get():
    """Get the current authenticated user"""
    return {"status": "ok", "user": current_user.as_dict(include_personal_data=True)}
