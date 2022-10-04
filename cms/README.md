## Goals

Build a wiki API with all common features, regardless of the content of documents

* [x] All basic user features
  * [x] create
  * [x] validate email
  * [x] login
  * [x] logout
  * [x] user name and email uniqueness
  * [x] send email to validate email address
  * [x] GET /current_user
* [x] modify user
  * [x] modify password
  * [x] modify email
  * [x] send email to validate email address
* [x] password reset
  * [x] password reset entry point and logic
  * [x] send email with a login token
  * [x] login token can only be used once
  * [x] login token must expire after one hour
* [x] rate limiting
  * [x] configurable
  * [x] use redis
* [x] unique document type, shipping a namespace field.
  * [x] `/documents`
    * [x] add a document
    * [x] get list of document
      * [x] offset and limit feature
  * [x] `/document` get, modify, delete a document
    * [x] Modify document
    * [x] manage edit conflict
    * [x] use redis
  * [x] `/versions`
    * [x] get a list of version
    * [x] all changes
    * [x] all changes related to one document
    * [x] all changes made by one user
    * [x] offset and limit feature
  * [x] `/version` get a given version of a doc
* [x] cooker
  * [x] documents can be cooked by a custom cook function
  * [x] they are served cooked by default everywhere
  * [x] cooker can get other documents
  * [x] if a document needs other documents to be cooked, a modification on one of those other document recompute the cache
* [x] Moderator options
  * [x] protect/unprotect a document
  * [x] hide/unhide a document version
  * [x] block/unblock an user
* [x] Admin options
  * [x] promote/unpromote an user to any role
  * [x] delete a document
  * [x] delete a document version
* [x] logs
  * [x] block/unblock user
  * [x] protect/unprotect document
  * [x] hide/unhide version
  * [x] delete a document
  * [x] delete a document version
* [x] user flag: any user can add any flag/value to any document
  * [x] get all document with some user flag ? /documents?flag=XX
  * [x] get all versions on document with an user flag ? `/versions?flag=XX` (AKA follow list ?)
* [ ] Customization
  * [x] define custom schema for document
  * [x] define custom schema for any route ?
  * [x] define custom cooker
  * [ ] define deletion rules
  * [ ] before save hook
  * [ ] before user creation savee hook

## TODO

forbid narcissus
user profile page
search must be configurable
cooker conf
redis conf
admin can rename user
more test on delete
more test on logs
more test!
user can delete option
before_document_delete hook
after_user_creation_hook
before_user_creation_hook
after_document_creation_hook
before_document_creation_hook
after_document_modification_hook
before_document_modification_hook
set an expiration date in redis for documents



## Golden rules

Here is a list of golden rules.

1. 100% test coverage : test is ok <=> you can release
2. explicit is better than implicit
3. keep it stupid and simple
4. Do not reinvent the wheel
5. 80/20 usage: Do the 80%. DON'T do the 20%
6. keep round API
7. API is security/consitency, UI is usability
8. security: everything is forbidden, except if it's allowed

## Stack

Do not re-invent the wheel as a golden rule. So it uses : 

* Flask
* Flask-Limiter
* Flask-Login
* Flask-Mail
* Flask-SQLAlchemy
* SQLAlchemy
* jsonschema
* redis
* postgresql
* nginx, uwsgi and haproxy for prod tools (even if you can use another one)

And on develpment side :

* pytest and pytest-cov
* black
* pylint
* freezegun

### Why not Flask-restful?

It's not maintenaind anymore : https://github.com/flask-restful/flask-restful/issues/883

And it turns out that flask handle pretty well json requests and response out-of-the-box. Furthermore, a rest framework adds some opiniated choices that can be imcompatible with orher well known flask plugin. So let's try with raw flask. As now, the only code we had to add is the exception handler.


## Target archi 

* Add/modify document
  * update DB
  * build document JSON
  * update Redis with the serialized document
* get document -> get in redis
* get list of document -> get ids in PG, values in redis
