from __future__ import annotations

import os
from typing import Any, Callable

from .chunking import compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            persist_dir = os.getenv("CHROMA_PERSIST_DIR")
            client = (
                chromadb.PersistentClient(path=persist_dir)
                if persist_dir
                else chromadb.EphemeralClient()
            )
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            # Không có chromadb, hoặc khởi tạo hỏng -> chạy hoàn toàn trong bộ nhớ.
            self._use_chroma = False
            self._collection = None

    @staticmethod
    def _matches(metadata: dict[str, Any], metadata_filter: dict[str, Any]) -> bool:
        """True khi metadata khớp TẤT CẢ cặp khoá-giá trị trong bộ lọc.

        So sánh cả dạng gốc lẫn dạng chuỗi: front matter parse ra `"2026"` còn
        bộ lọc viết trong YAML có thể là số `2026`, hai giá trị đó nên khớp nhau.
        """
        for key, expected in metadata_filter.items():
            actual = metadata.get(key)
            if actual != expected and str(actual) != str(expected):
                return False
        return True

    def _make_record(self, doc: Document) -> dict[str, Any]:
        meta = dict(doc.metadata)
        meta.setdefault("doc_id", doc.id)
        return {
            "id": f"{doc.id}::{self._next_index}",
            "content": doc.content,
            "metadata": meta,
            "embedding": self._embedding_fn(doc.content)
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_vector = self._embedding_fn(query)
        scored = []
        for record in records:
            score = compute_similarity(query_vector, record["embedding"])
            scored.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": score
            })
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return
        for doc in docs:
            record = self._make_record(doc)
            self._next_index += 1
            self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if metadata_filter is None:
            return self.search(query, top_k)
            
        filtered_records = []
        for record in self._store:
            match = True
            for k, v in metadata_filter.items():
                if record["metadata"].get(k) != v:
                    match = False
                    break
            if match:
                filtered_records.append(record)
                
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        original_size = len(self._store)
        self._store = [r for r in self._store if not (
            r["metadata"].get("doc_id") == doc_id or 
            r["id"] == doc_id or 
            r["id"].startswith(f"{doc_id}::")
        )]
        return len(self._store) < original_size
