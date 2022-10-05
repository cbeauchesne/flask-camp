""" Views related to account operations """

from flask import request, current_app

from wiki_api.decorators import allow
from wiki_api.models.user import User as UserModel
from wiki_api.schemas import schema


rule = "/reset_password"


@allow("anonymous", "authenticated")
@schema("reset_password.json")
def post():
    """Send an email with a login token to this user"""
    email = request.get_json()["email"]

    user = UserModel.get(_email=email)

    if user is None:  # do not let hacker crawl our base
        fake_user = UserModel()
        fake_user.set_login_token()

        return {"status": "ok", "expiration_date": fake_user.login_token_expiration_date.isoformat()}

    user.set_login_token()

    current_app.database.session.commit()

    user.send_login_token_mail()

    return {"status": "ok", "expiration_date": user.login_token_expiration_date.isoformat()}
