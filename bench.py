import yaml
from ingest import build_knowledge_base
from src.chunking import SentenceChunker
from src.embeddings import LocalEmbedder
from src.agent import KnowledgeBaseAgent

def mock_llm(prompt: str) -> str:
    preview = prompt[prompt.find("Context:") : prompt.find("Question:")].replace("\n", " ")[:200]
    return f"[DEMO LLM] Generated answer from prompt preview: {preview}..."

import sys
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    # 1. Chọn chunker của riêng bạn (Role 3 -> SentenceChunker)
    print("Khởi tạo SentenceChunker")
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    embedding_fn = LocalEmbedder()

    # 2. Nạp cả thư mục corpus
    print("Đang nạp dữ liệu vào store...")
    store = build_knowledge_base("data/k3_university", embedding_fn, chunker=chunker)
    agent = KnowledgeBaseAgent(store, mock_llm)

    print(f"Đã nạp {store.get_collection_size()} chunks.\n")

    # Đọc câu hỏi từ YAML
    with open("data/benchmark_queries.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # 3. Chạy 5 query
    for q in data["queries"]:
        qid = q["id"]
        question = q["question"]
        m_filter = q.get("metadata_filter")
        
        print(f"=== {qid} ===")
        print(f"Câu hỏi: {question}")
        if m_filter:
            print(f"Lọc (Filter): {m_filter}")
        
        results = store.search_with_filter(question, top_k=3, metadata_filter=m_filter)
        
        print("Top-3 chunks:")
        for i, r in enumerate(results, 1):
            doc_id = r['metadata'].get('doc_id', 'unknown')
            score = r['score']
            preview = r['content'].replace("\n", " ")[:100]
            print(f"  {i}. score={score:.3f} source={doc_id}")
            print(f"     {preview}...")
            
        answer = agent.answer(question, top_k=3)
        print(f"Agent: {answer}\n")

if __name__ == "__main__":
    main()
