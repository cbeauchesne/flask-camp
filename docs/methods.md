## Methods behavior guidelines

* `GET`: Get some data, no midification on database
* `POST`: Modify some existing data without aadding any row to database
* `PUT`: Add a new row in database
* `DELETE`: Delete a row in database

## Exceptions

* `POST /document/<document_id>` actually add a row in the database. But from user perspective, it does not create a document
* `POST /user_tags` can create the user tag if it does not exists
