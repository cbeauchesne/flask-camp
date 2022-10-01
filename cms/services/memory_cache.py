import json
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

    def set_document(self, document_id, document_as_dict, cooked_document_as_dict):
        self._document.set(document_id, {"document": document_as_dict, "cooked_document": cooked_document_as_dict})

    def get_document(self, document_id):
        result = self._document.get(document_id)

        return None if result is None else result["document"]

    def get_cooked_document(self, document_id):
        result = self._document.get(document_id)

        return None if result is None else result["cooked_document"]

    def delete_document(self, document_id):
        self._document.delete(document_id)

    def flushall(self):
        self._client.flushall()

    def create_index(self):
        schema = (
            TagField("$.document.protected", as_name="protected"),
            TagField("$.document.namespace", as_name="namespace"),
            NumericField("$.document.user.id", as_name="last_user"),
            NumericField("$.document.id", as_name="document_id"),
        )

        self._document.search_engine.create_index(
            schema, definition=IndexDefinition(prefix=["document:"], index_type=IndexType.JSON)
        )

    def search(self, offset=0, limit=30):

        # args = []

        # TODO injection mightmare
        # if namespace is not None:
        #     args.append(f"@namespace:{{{namespace}}}")

        query = Query("*").paging(offset, limit)
        result = self._document.search_engine.search(query)

        log.info(query.query_string())

        s = {
            "status": "ok",
            "count": result.total,
            "documents": [json.loads(doc.json)["cooked_document"] for doc in result.docs],
        }

        return s

    # search an array
    # schema = (TagField("$.*", as_name="array"),)

    # self._association.search_engine.create_index(
    #     schema, definition=IndexDefinition(prefix=["association:"], index_type=IndexType.JSON)
    # )

    # def get_dependants(self, document_id):
    #     query = Query(f"@array:{{{document_id}}}")
    #     result = self._association.search_engine.search(query)

    #     return [int(doc.id[12:]) for doc in result.docs]
