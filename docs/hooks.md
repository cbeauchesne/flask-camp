`hooks` are user defined function called during a requests. They usually come by pair : 

* `before_<some_event>`: They will be called just before committing a transaction with flask_camp models as arguments. You can raise any `werkzeug.exception` to prevent the operation to happen, or modify whatever you need. They return nothing
* `after_<some_event>`: They will be called just before returning the HTTP response, and the argument will be a `JsonResponse`

## `before_create_document(document: Document)` and `after_create_document(response: JsonResponse)`

* When: `POST /documents`

## `after_get_document(response: JsonResponse)`

* When: `GET /document/<int:document_id>`

## `after_get_documents(response: JsonResponse)`

* When: `GET /documents`

## `before_update_document(document, old_version, new_version)`

* When: 
  * `POST /document/<int:document_id>` : when a new version is added
  * `PUT /version/<int:version_id>` : when a new version is hidden/unhidden, and the last version of the document is changed
  * `PUT /documents/merge` : when a two document are merged, and the last version of the destination becomes the version of the merged document
