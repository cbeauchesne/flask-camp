## Goals

Build a wiki API with all common features, regardless of the content of documents

* [ ] All basic user features
  * [x] create
  * [x] validate email
  * [x] login
  * [x] logout
  * [x] user name and email uniqueness
  * [ ] send email to validate email address
* [ ] modify user
  * [x] modify password
  * [x] modify email
  * [ ] send email to validate email address
* [ ] password reset
  * [x] password reset entry point and logic
  * [ ] send email with a login token
  * [x] login token can only be used once
  * [x] login token must expire after one hour
* [x] rate limiting
  * [x] rate limiting on user login failures
  * [x] rate limiting on document creation
  * [x] rate limiting on document modification
* [x] unique document type, shipping a namespace field.
  * [x] document can be protected by moderators
* [ ] document list
  * [x] get
  * [x] offset and limit feature
  * [ ] use elasticsearch
* [ ] Modify
  * [x] Modify document
  * [ ] manage edit conflict
  * [x] get a given version
* [x] document history
  * [x] all changes
  * [x] all changes related to one document
  * [x] all changes made by one user
  * [x] offset and limit feature
  * [x] an item in the history can be hidden by moderators
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
* [ ] user flag: any user can add any flag/value to any document
  * [x] get all document with some user flag ? /documents?flag=XX
  * [ ] get all changes on document with an user flag ? /changes?flag=XX (AKA follow list ?)


## TODO
Test rate limiter
more test on delete
more test on logs

## Golden rules

* keep round API
* explicit is better than implicit
* 100% test coverage : test is ok <=> you can release
* 80/20 usage: Do the 80%. do NOT the 20%
* Do not reinvent the wheel
* API is security/consitency, UI is usability
* security: everything is forbidden, except if it's allowed

## Stack

Do not re-invent the wheel as a golden rule. So it uses : 

* Flask
* Flask-Limiter
* Flask-Login
* SQLAlchemy
* jsonschema

And on develpment side :

* pytest and pytest-cov
* black
* pylint
* freezegun

### Why not Flask-restful

It's not maintenaind anymore : https://github.com/flask-restful/flask-restful/issues/883

And it turns out that flask handle pretty well json requests and response out-of-the-box. Furthermore, a rest framework adds some opiniated choices that can be imcompatible with orher well known flask plugin. So let's try with raw flask. As now, the only code we had to add is the exception handler.


## Target archi 

* Add/modify document
  * update DB
  * build document JSON
  * update Elasticsearch with the serialized document
* get document -> get in elastic search
* get list of document -> get in elastic search
* get list of document with filters -> get in elastic search
