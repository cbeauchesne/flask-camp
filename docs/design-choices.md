## Why users are identified by their names instead of their id?

Because names are importants in a wiki. It create the identity of their owner. Changing name introduce some blur.... TODO

## Why not having user name as identifiers, instead of id?

Yes it makes prettier URL. But it requires extra complexity in SQL

## Why having a dedicated search index and collection, rather than using document: or cooked_document: in Redis ?

* it allows `document:` and `cooked_document:` to be not totally correlated with DB
* we can use the tag system for numeric values
* when you need to modify a doc that is used to build lot of document, you can simple remove all of them from redis, rather than recomputing everything