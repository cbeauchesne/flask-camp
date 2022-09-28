## Status

* 200: the request has been successfully executed
* 301: redirection
* 401: Unauthorized: only for login failures
* 403: if the users (anonymous or not) lacks some role to perform the request
* 404: Not found
* 405: Method not allowed on this endpoint
* 409: Conflict, user is trying to edit a document but a new version has been published

## Ressources

* https://stackoverflow.com/questions/3297048/403-forbidden-vs-401-unauthorized-http-responses
