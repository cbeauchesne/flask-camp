## Goals

Build a wiki api with all common features, regardless of the content of documents

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
* [ ] document history
  * [ ] all changes
  * [ ] all changes related to one document
  * [ ] all changes made by one user
* [ ] follow list

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
