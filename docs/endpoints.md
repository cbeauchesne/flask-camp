* `GET /`: Display the possible route for this API
* `GET /document/<int:document_id>`: Get a document
* `POST /document/<int:document_id>`: Add a new version to a document
* `PUT /document/<int:document_id>`: Modify a document. Actually, only protect/unprotect it is possible
* `DELETE /document/<int:document_id>`: Delete a document
* `GET /document/version<int:version_id>`: Get a given version of a document
* `PUT /document/version<int:version_id>`: Modify a version of a document. The only possible modification is hide/unhide a version
* `DELETE /document/version<int:version_id>`: Delete a version of a document (only for admins)
* `GET /documents`: Get a list of documents
* `POST /documents`: Create an document
* `PUT /documents/merge`: Merge two documents. Merged document will become a redirection, and will be no longer modifiable
    Other document will get all history from merged
* `GET /documents/versions`: Get a list of versions
* `GET /healthcheck`: Ping? pong!
* `GET /logs`: Return a list of logs
* `GET /user/<int:user_id>`: Get an user
* `PUT /user/<int:user_id>`: Modify an user
* `GET /user/current`: Get the current authenticated user
* `PUT /user/login`: Login an user
* `DELETE /user/login`: Logout current user
* `PUT /user/reset_password`: Send an email with a login token to this user
* `GET /user/validate_email`: Resend validation mail to an user. Only admin can do this request
* `PUT /user/validate_email`: Validate an user's email
* `GET /user_tags`: Get user tag list
* `POST /user_tags`: create/modify an user tag
* `DELETE /user_tags`: Delete an user tag
* `GET /users`: Get a list of users
* `POST /users`: Create an user
