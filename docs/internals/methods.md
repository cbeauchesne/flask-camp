## Methods behavior guidelines

Flask-camp uses 4 differents HTTP methods : `GET`, `POST`, `PUT` and `DELETE`.

`GET` and `DELETE` are straightforward: you get, or delete the ressource described by th URI.

On the other hand, `POST` and `PUT` roles are [often blurry on REST API](https://www.google.com/search?q=Rest+API+post+put). We follow here a key principle : `PUT` is [idempotent](https://en.wikipedia.org/wiki/Idempotence), `POST` is not. 

* `PUT` : several identical calls will have the same effect. Nothing is added in database, only modification of existing records are made.
* `POST` : A successful call will add a new row in the database.

Here is the exhaustive list of `POST`/`PUT` class, with their purpose:

* `POST /documents`  -> add new document
* `POST /document/<i>` -> add a new version to the document i
* `PUT  /document/<i>` -> modify document i. Only protection is possible
* `PUT  /document/version<i>` -> modify version i. Only hide is possible
* `PUT  /documents/merge` -> it modify TODO consider PATCH
* `POST /users` -> add a new user
* `PUT  /user/i` -> update user i. It's a partial update, only properties sent are updated,  TODO consider PATCH
* `PUT  /user/validate_email`
* `PUT  /user/reset_password`
* `PUT  /user/login`

*Note*: logs are not considered, any call using any method can create a log row.
