import logging

from redis import Redis as RedisClient
from redis.commands.json.path import Path
from redis.commands.search.field import TagField, NumericField  # , TextField,
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query  # , NumericFilter


log = logging.getLogger(__name__)


class _MemoryCacheCollection:
    def __init__(self, name, client):
        self.name = name
        self._client = client.json()
        self.search_engine = client.ft(name)

    def get(self, document_id):
        return self._client.get(f"{self.name}:{document_id}")

    def set(self, id, document):
        self._client.set(f"{self.name}:{id}", Path.root_path(), document)

    def delete(self, id):
        self._client.delete(f"{self.name}:{id}")


class MemoryCache:
    def __init__(self, host, port):
        self._client = RedisClient(host=host, port=port)

        self._document = _MemoryCacheCollection("document", self._client)
        self._cooked_document = _MemoryCacheCollection("cooked_document", self._client)
        self._association = _MemoryCacheCollection("association", self._client)

    def set_document(self, document_id, document_as_dict, cooked_document_as_dict, associated_ids):
        self._document.set(document_id, document_as_dict)
        self._cooked_document.set(document_id, cooked_document_as_dict)

        self._association.set(document_id, [str(associated_id) for associated_id in associated_ids])

    def get_document(self, document_id):
        return self._document.get(document_id)

    def get_cooked_document(self, document_id):
        return self._cooked_document.get(document_id)

    def delete_document(self, document_id):
        self._document.delete(document_id)
        self._cooked_document.delete(document_id)

    def flushall(self):
        self._client.flushall()

    def create_index(self):
        schema = (
            TagField("$.protected", as_name="protected"),
            TagField("$.namespace", as_name="namespace"),
            NumericField("$.user.id", as_name="last_user"),
            NumericField("$.id", as_name="document_id"),
            # NumericField("$.b", as_name="b"),
            # TagField("$.array.*", as_name="array"),
        )

        self._cooked_document.search_engine.create_index(
            schema, definition=IndexDefinition(prefix=["cooked_document:"], index_type=IndexType.JSON)
        )

        schema = (TagField("$.*", as_name="array"),)

        self._association.search_engine.create_index(
            schema, definition=IndexDefinition(prefix=["association:"], index_type=IndexType.JSON)
        )

    def get_dependants(self, document_id):
        query = Query(f"@array:{{{document_id}}}")
        result = self._association.search_engine.search(query)

        return [int(doc.id[12:]) for doc in result.docs]

    def search(self, offset=0, limit=30):

        # args = []

        # TODO injection mightmare
        # if namespace is not None:
        #     args.append(f"@namespace:{{{namespace}}}")

        query = Query("*").paging(offset, limit)
        result = self._cooked_document.search_engine.search(query)

        log.info(query.query_string())

        # magic
        s = ",".join([doc.json for doc in result.docs])
        s = f'{{"status": "ok", "count": {result.total}, "documents": [{s}]}}'

        return s
