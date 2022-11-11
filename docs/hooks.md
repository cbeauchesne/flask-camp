`hooks` are user defined function called during a requests. They usually come by pair : 

* `before_<some_event>`: They will be called just before committing a transaction with flask_camp models as arguments. You can raise any exception here to prevent the operation to happen, or modify whatever you need. They return nothing
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



This hooks will be called before each new version is saved. `document` is a `Document` instance, and both `old_version` and `new_version` are `DocumentVersion` instance.

It covers three use cases : 

1. creation, where `old_version` is `None`
2. regular new version, where both `old_version` and `new_version` are not `None`
3. merge, where `new_version` is `None` for the merged document. If the last version does not change for the destination, the function is not called.
4. if the last version is deleted, the function will be called with the new most recent (not hidden) version as `new_version`. `old_version` will contains the deleted version.
5. if the last version is hidden, the function will be called with the new most recent (not hidden) version as `new_version`. `old_version` will contains the newly hidden  version.

To prevent the action to perform, you can raise any `werkzeug.exception`.
