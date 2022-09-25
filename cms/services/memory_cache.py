import json


class _MemoryCacheCollection:
    def __init__(self, name, client):
        self.name = name
        self._client = client

    def get(self, document_id):
        r = self._client.get(f"{self.name}:{document_id}")
        return r if r is None else json.loads(r)

    def set(self, id, document):
        self._client.set(f"{self.name}:{id}", json.dumps(document))

    def delete(self, id):
        self._client.delete(f"{self.name}:{id}")


class MemoryCache:
    def __init__(self, client):
        self._client = client
        self.document = _MemoryCacheCollection("document", self._client)

    def flushall(self):
        self._client.flushall()
