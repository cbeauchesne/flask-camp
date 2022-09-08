User creation and password reset follow this process

## User creation

1. User give a name, an email and a password via `PUT /users` Email is stored as NOT validated
2. A one-usage token is generated and sent to the user via a mail as a UI link like `/validate_email?name=xx&token=yy`
3. The UI is responsaible to do a `POST /validate_email` with username/token present in the request query
4. The email is validated, and the token is removed. User is not logged in

## Email change

Possible if and only if email is validated, and if the user is logged

1. user gives a new email with `/POST /user/<user_id>`, it is stored as not validated.
2. A one-usage token is generated and sent to the user via a mail as a UI link like `/validate_email?name=xx&token=yy`
3. The UI is responsible to do a `POST /validate_email` with the username/token present in the request query
5. the new email is validated and the token is removed

## Password reset

1. as an anonymous user, the UI send a `POST /reset_password` with the mail
2. if the mail does not exists, or is not validated, the process stops (though, a normal response is sent)
3. A one-usage token is generated and sent to the user via a mail as a UI link like `/login?name=xx&token=yy`
4. The UI is responsible to do a `POST /login` with the username/token present in the request query
5. User is logged, and the token is removed.
6. UI is reponsible to show a password reset page