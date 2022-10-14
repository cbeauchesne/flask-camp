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


class _MemoryCache:
    def __init__(self):
        self._client = None
        self._document = None

    def init_app(self, app):
        host = app.config.get("REDIS_HOST", "localhost")
        port = app.config.get("REDIS_PORT", 6379)

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

    @property
    def client(self):
        return self._client


memory_cache = _MemoryCache()
