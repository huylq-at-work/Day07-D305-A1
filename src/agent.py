from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy dữ liệu liên quan."
            
        context_parts = []
        for i, result in enumerate(results, 1):
            doc_id = result["metadata"].get("doc_id", "unknown")
            context_parts.append(f"[{i}] ({doc_id}) {result['content']}")
            
        context_str = " ".join(context_parts)
        
        prompt = (
            "Instruction: chỉ dùng context; nói rõ khi context không đủ.\n"
            f"Context: {context_str}\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
