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
  * [ ] password reset using validated email
* [ ] rate limiting
* [x] unique document type, shipping a namespace field.
* [ ] document list
  * [x] get
  * [x] offset and limit feature
* [ ] Modify
  * [x] Modify document
  * [ ] manage edit conflict
* [x] document history
  * [x] all changes
  * [x] all changes related to one document
  * [x] all changes made by one user
  * [x] offset and limit feature
* [ ] Moderator options
  * protect/unprotect a document
  * hide/unhide a document version
  * block/unbloc an user
* [ ] Admin options
  * [x] promote/unpromote an user to any role
* [ ] follow list: get all changes made to documents in the user's follow list
* [ ] logs
  * [ ] All admin/moderator actions
* [ ] user flag: any user can add any flag/value to any documentx

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
