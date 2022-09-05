## Goals

Build a wiki API with all common features, regardless of the content of documents

* basic user features
  * [x] create
  * [x] validate email
  * [x] login
  * [x] logout
  * [ ] modify user
     * [x] modify password
     * [ ] modify email
     * [ ] rate limiting on user login failures
* [x] unique document type, shipping a namespace field.
* [ ] get document list
* [ ] Modify document
  * [ ] manage edit conflict
* [ ] document history
  * [ ] all changes
  * [ ] all changes related to one document
  * [ ] all changes made by one user
* [ ] Moderator options
  * protect/unprotect a document
  * hide/unhide a document version
  * block/unbloc an user
* [ ] Admin options
  * [ ] promote/unpromote an user to moderator
* [ ] follow list: get all changes made to documents in the user's follow list
* [ ] logs
  * [ ] All admin/moderator actions

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
