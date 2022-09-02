Functionnal target : 

outings with raw text content
document history
recent change



Requirements

Recent change
   doc id/type
   version
   comment
   timestamp
   author

get version
    doc id type
    version




<Document>
    id
    type
    protected

<DocumentVersion>
    id  -> version id
    document_id -> Document.id
    hidden  # only mutable field

    



    author_id
    timestamp
    comment

    childs[]
    ...

Associations
    parent_id
    child_id

