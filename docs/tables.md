Document
    id
    last_version_id
    protected

<DocumentType>
    id
    document_id -> Document.id
    hidden  # only mutable field
    childs[]
    ...

Change
    id
    document_id -> Document.id
    version_id -> <DocumentType>.id
    author_id
    timestamp
    comment
    