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
        """Chuẩn hoá một Document thành bản ghi lưu trữ (nhúng đúng MỘT lần)."""
        metadata = dict(doc.metadata or {})
        metadata.setdefault("doc_id", doc.id)
        record = {
            "index": self._next_index,
            "id": doc.id,
            "content": doc.content,
            # Copy để store không dùng chung dict với Document bên ngoài:
            # người gọi sửa metadata sau đó sẽ không âm thầm đổi dữ liệu đã nạp.
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Xếp hạng `records` theo độ tương tự cosine với `query`."""
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)
        scored = [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": compute_similarity(query_embedding, record["embedding"]),
            }
            for record in records
        ]
        # Chốt hạng bằng (điểm giảm dần, thứ tự nạp tăng dần): hai chunk cùng điểm
        # luôn ra cùng một thứ tự giữa các lần chạy, nếu không thì rank_of_gold
        # trong benchmark sẽ nhảy lung tung mà không ai giải thích được.
        order = {id(item): record["index"] for item, record in zip(scored, records)}
        scored.sort(key=lambda item: (-item["score"], order[id(item)]))
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        records = [self._make_record(doc) for doc in docs]
        self._store.extend(records)

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.add(
                    # doc_id trùng nhau giữa các chunk là chuyện bình thường,
                    # nên khoá của Chroma phải kèm số thứ tự nạp.
                    ids=[f"{r['id']}#{r['index']}" for r in records],
                    documents=[r["content"] for r in records],
                    embeddings=[r["embedding"] for r in records],
                    metadatas=[r["metadata"] or {"_": ""} for r in records],
                )
            except Exception:
                # Chroma hỏng thì bản trong bộ nhớ vẫn đủ dùng — không làm sập lab.
                self._use_chroma = False

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
        if not metadata_filter:
            return self._search_records(query, self._store, top_k)

        # LỌC TRƯỚC rồi mới xếp hạng. Nếu xếp hạng trước rồi lọc sau thì bộ lọc
        # chỉ tỉa phần đuôi của top_k, và chunk đúng nằm ngoài top_k vẫn mất.
        candidates = [r for r in self._store if self._matches(r["metadata"], metadata_filter)]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        def belongs_to(record: dict[str, Any]) -> bool:
            # Ba cách một chunk thuộc về một tài liệu:
            #   metadata['doc_id']  -> đường đi qua ingest.build_knowledge_base()
            #   id trùng nguyên     -> Document nạp trực tiếp, chưa chia chunk
            #   id dạng "<doc>::chunk_N" -> quy ước đặt tên của ingest.chunk_document()
            return (
                record["metadata"].get("doc_id") == doc_id
                or record["id"] == doc_id
                or record["id"].startswith(f"{doc_id}::")
            )

        removed = [r for r in self._store if belongs_to(r)]
        if not removed:
            return False

        self._store = [r for r in self._store if not belongs_to(r)]
        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(ids=[f"{r['id']}#{r['index']}" for r in removed])
            except Exception:
                self._use_chroma = False
        return True
