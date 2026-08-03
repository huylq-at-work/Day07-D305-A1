from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
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
            import chromadb
            
            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        return {
            'id': doc.id,
            'content': doc.content,
            'embedding': embedding,
            'metadata': doc.metadata
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not records:
            return []
        
        query_embedding = self._embedding_fn(query)
        
        # Compute similarity scores
        scored_records = []
        for record in records:
            score = _dot(query_embedding, record['embedding'])
            scored_records.append({
                'content': record['content'],
                'metadata': record['metadata'],
                'score': score
            })
        
        # Sort by score descending and return top_k
        scored_records.sort(key=lambda x: x['score'], reverse=True)
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return
        
        if self._use_chroma and self._collection is not None:
            ids = [doc.id for doc in docs]
            documents = [doc.content for doc in docs]
            embeddings = [self._embedding_fn(doc.content) for doc in docs]
            metadatas = [doc.metadata for doc in docs]
            
            self._collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
        else:
            for doc in docs:
                record = self._make_record(doc)
                self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Convert ChromaDB results to standard format
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, content in enumerate(results['documents'][0]):
                    search_results.append({
                        'content': content,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'score': 1.0 - results['distances'][0][i] if results['distances'] else 1.0
                    })
            return search_results
        else:
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        else:
            return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            
            where_clause = metadata_filter if metadata_filter else None
            
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            # Convert ChromaDB results to standard format
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, content in enumerate(results['documents'][0]):
                    search_results.append({
                        'content': content,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'score': 1.0 - results['distances'][0][i] if results['distances'] else 1.0
                    })
            return search_results
        else:
            # In-memory filtering
            filtered_records = self._store
            
            if metadata_filter:
                filtered_records = [
                    record for record in self._store
                    if all(record['metadata'].get(k) == v for k, v in metadata_filter.items())
                ]
            
            return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            try:
                # Try to get the document first to check if it exists
                existing = self._collection.get(ids=[doc_id])
                if existing and existing['ids']:
                    self._collection.delete(ids=[doc_id])
                    return True
                return False
            except Exception:
                return False
        else:
            # In-memory deletion
            original_size = len(self._store)
            self._store = [record for record in self._store if record['id'] != doc_id]
            return len(self._store) < original_size
