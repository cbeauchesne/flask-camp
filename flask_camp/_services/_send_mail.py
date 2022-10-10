from flask import current_app
from flask_mail import Mail, Message


class SendMail(Mail):
    def send_account_creation(self, email, token, user):
        current_app.logger.info("Send registration mail to user %s", user.name)
        message = Message(
            "Welcome to example.com",  # TODO
            recipients=[email],
            body=f"https://example.com?email_token={token}",
            html=f'<a href="https://example.com?email_token={token}">click</a>',
        )

        self.send(message)

    def send_email_change(self, email, token, user):
        current_app.logger.info("Send mail address update mail to user %s", user.name)
        message = Message(
            "Change email",  # TODO
            recipients=[email],
            body=f"https://example.com?email_token={token}",
            html=f'<a href="https://example.com?email_token={token}">click</a>',
        )

        self.send(message)

    def send_login_token(self, email, token, user):
        current_app.logger.info("Send login token mail to user %s", user.name)
        message = Message(
            "Login token email",  # TODO
            recipients=[email],
            body=f"https://example.com?login_token={token}",
            html=f'<a href="https://example.com?login_token={token}">click</a>',
        )

        self.send(message)
