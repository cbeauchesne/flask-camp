## Why not having user name as identifiers, instead of id?

Yes it makes prettier URL. But renaming is always possible (even if it's an admin action). It would ask to update all versions made by the user in database 

## Why having a dedicated search index and collection, rather than using document: in Redis ?

* it allows `document:` collection to be not fully filled, only be document often used
* we can use the tag system for numeric values (REDIS limitation)
* when you need to modify a doc that is used to build lot of document, you can simple remove all of them from redis, rather than recomputing everything

## Why clearing memory cache on each modification, rather than updating it

First of all, a document can be used by thousand other documents. We can't update all of them : 

* A `POST /document` would take a while...
* ... for probably nothing, if most of those dependant are not requested between two modif on parent doucment

So we clear them from the memory cache, and a `GET` will pay the unitary cost

> Ok, but why not at least update the memory cache for the updated document only ? 

Because we need to deeply think of any race condition that can corrupt the memory cache before, TO BE DONE...
