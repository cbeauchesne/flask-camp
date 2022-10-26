## 'on_document_save(document, old_version, new_version)'

This hooks will be called befaore each new version is saved. `document` is a `Document` instance, and both `old_version` and `new_version` are `DocumentVersion` instance.

It covers three use cases : 

1. creation, where `old_version` is `None`
2. regular new version, where both `old_version` and `new_version` are not `None`
3. merge, where `new_version` is `None` for the merged document. If the last version does not change for the destination, the function is not called.
4. if the last version is deleted, the function will be called with the new most recent (not hidden) version as `new_version`. `old_version` will contains the deleted version.
5. if the last version is hidden, the function will be called with the new most recent (not hidden) version as `new_version`. `old_version` will contains the newly hidden  version.

To prevent the action to perform, you can raise any `werkzeug.exception`.
