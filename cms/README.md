## Goals

Build a wiki API with all common features, regardless of the content of documents

* [ ] basic user features
  * [x] create
  * [x] validate email
  * [x] login
  * [x] logout
  * [x] user name and email uniqueness
  * [ ] modify user
    * [x] modify password
    * [x] modify email
    * [ ] send email to validate email address
  * [ ] rate limiting on user login failures
  * [ ] password reset
    * [x] password reset entry point and logic
    * [ ] send email with a login token
    * [ ] login token must expire after one hour
* [ ] rate limiting
* [x] unique document type, shipping a namespace field.
  * [x] document can be protected by moderators
* [ ] document list
  * [x] get
  * [x] offset and limit feature
* [ ] Modify
  * [x] Modify document
  * [ ] manage edit conflict
* [ ] document history
  * [x] all changes
  * [x] all changes related to one document
  * [x] all changes made by one user
  * [x] offset and limit feature
  * [ ] an item in the history can be hidden by moderators
* [ ] Moderator options
  * [x] protect/unprotect a document
  * [ ] hide/unhide a document version
  * [x] block/unbloc an user
* [ ] Admin options
  * [x] promote/unpromote an user to any role
* [ ] follow list: get all changes made to documents in the user's follow list
* [x] logs
  * [x] All admin/moderator actions
* [ ] user flag: any user can add any flag/value to any document


## Golden rules

* keep round API
* explicit is better than implicit
* 100% test coverage : test is ok <=> you can release
* 80/20 usage: Do the 80% do NOT the 20%
* Do not reinvent the wheel
* API is security/consitency, UI is usability
* security: everything is forbidden, except if it's allowed

## Stack

Do not re-invent the wheel as a golden rule. So it uses : 

* Flask
* Flask-restful
* Flask_login
* SQLAlchemy
* jsonschema

And on develpment side :

* black
* pylint

## Target archi 

* Add/modify document
  * update DB
  * build document JSON
  * update Elasticsearch with the serialized document
* get document -> get in elastic search
* get list of document -> get in elastic search
* get list of document with filters -> get in elastic search
