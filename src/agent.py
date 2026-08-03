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

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict | None = None) -> str:
        results = self.store.search_with_filter(
            question, top_k=top_k, metadata_filter=metadata_filter
        )

        if not results:
            # Không bịa khi kho tri thức không có gì liên quan. Câu "không biết"
            # đúng lúc là hành vi đúng của RAG, không phải thất bại.
            return (
                "Không tìm thấy thông tin liên quan trong cơ sở tri thức "
                "để trả lời câu hỏi này."
            )

        # Đánh số nguồn để câu trả lời truy vết được về đúng chunk nào.
        context = "\n\n".join(
            f"[{index}] (nguồn: {result['metadata'].get('doc_id', result['id'])}, "
            f"score={result['score']:.3f})\n{result['content']}"
            for index, result in enumerate(results, start=1)
        )

        prompt = (
            "Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu được cung cấp.\n"
            "Chỉ dùng thông tin trong phần NGỮ CẢNH. Nếu ngữ cảnh không đủ để trả lời, "
            "hãy nói rõ là không đủ thông tin thay vì suy đoán.\n"
            "Khi trả lời, dẫn số nguồn [1], [2]... cho từng ý.\n"
            "Nếu các nguồn mâu thuẫn nhau, hãy nêu rõ mâu thuẫn đó.\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI: {question}\n\n"
            "TRẢ LỜI:"
        )
        return self.llm_fn(prompt)
