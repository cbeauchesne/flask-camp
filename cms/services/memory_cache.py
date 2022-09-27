from redis import Redis as RedisClient
from redis.commands.json.path import Path


class _MemoryCacheCollection:
    def __init__(self, name, client):
        self.name = name
        self._client = client.json()

    def get(self, document_id):
        return self._client.get(f"{self.name}:{document_id}")

    def set(self, id, document):
        self._client.set(f"{self.name}:{id}", Path.root_path(), document)

    def delete(self, id):
        self._client.delete(f"{self.name}:{id}")


class MemoryCache:
    def __init__(self, host, port, cooker):
        self._client = RedisClient(host=host, port=port)
        self._document = _MemoryCacheCollection("document", self._client)
        self._cooked_document = _MemoryCacheCollection("cooked_document", self._client)
        self.cooker = cooker

    def set_document(self, document_id, document_as_dict):
        # TODO : must not get document_as_dict
        self._document.set(document_id, document_as_dict)
        cooked_document = self.cooker(document_as_dict)
        self._cooked_document.set(document_as_dict["id"], cooked_document)

    def get_document(self, document_id):
        return self._document.get(document_id)

    def get_cooked_document(self, document_id):
        return self._cooked_document.get(document_id)

    def delete_document(self, document_id):
        self._document.delete(document_id)
        self._cooked_document.delete(document_id)

    def flushall(self):
        self._client.flushall()
