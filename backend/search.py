import os
from opensearchpy import OpenSearch

class SearchClient:
    def __init__(self, url: str | None = None):
        self.url = url or os.getenv('SEARCH_URL', 'http://localhost:9200')
        self.client = None
        try:
            self.client = OpenSearch(self.url)
        except Exception:
            self.client = None

    def healthy(self) -> bool:
        try:
            return bool(self.client and self.client.ping())
        except Exception:
            return False

    def index_listing(self, index: str, body: dict, id: str | None = None):
        if not self.client:
            return None
        return self.client.index(index=index, id=id, body=body)

    def search(self, index: str, query: dict):
        if not self.client:
            return {"hits": {"total": 0, "hits": []}}
        return self.client.search(index=index, body=query)
