"""Benchmark cá nhân Role 2 trên đúng 5 query chung của nhóm.

Pipeline giữ nguyên dữ liệu, query và embedding; biến chiến lược duy nhất là
HeadingChunker. Local embedding là tùy chọn nên lượt chạy core mặc định dùng
MockEmbedder và luôn in cảnh báo rằng điểm số không phản ánh ngữ nghĩa.
"""

from __future__ import annotations

import argparse
from typing import Any

from ingest import build_knowledge_base
from main import demo_llm
from scripts.custom_chunkers import HeadingChunker
from scripts.run_benchmark import load_queries
from src import KnowledgeBaseAgent, _mock_embed


class QueryStoreView:
    """Adapter để Agent dùng cùng metadata filter với lượt retrieval hiện tại."""

    def __init__(self, store, metadata_filter: dict[str, Any] | None) -> None:
        self.store = store
        self.metadata_filter = metadata_filter

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        if self.metadata_filter:
            return self.store.search_with_filter(
                query,
                top_k=top_k,
                metadata_filter=self.metadata_filter,
            )
        return self.store.search(query, top_k=top_k)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", default="data/k3_university")
    parser.add_argument("--queries", default="data/benchmark_queries.yaml")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--max-level", type=int, default=2)
    parser.add_argument("--max-chars", type=int, default=1200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.top_k <= 0 or args.max_level <= 0 or args.max_chars <= 0:
        raise SystemExit("top-k, max-level và max-chars phải lớn hơn 0.")

    queries = load_queries(args.queries)
    if len(queries) != 5:
        raise SystemExit(f"Benchmark cần đúng 5 query, hiện có {len(queries)}.")

    chunker = HeadingChunker(max_level=args.max_level, max_chars=args.max_chars)
    store = build_knowledge_base(
        args.docs,
        embedding_fn=_mock_embed,
        chunker=chunker,
        collection_name="role2_personal_heading",
    )

    print("=== BENCHMARK CÁ NHÂN — ROLE 2 ===")
    print("strategy=heading")
    print(f"params=max_level={args.max_level},max_chars={args.max_chars}")
    print(f"embedding_backend={_mock_embed._backend_name}")
    print(f"n_chunks_total={store.get_collection_size()}")
    print(
        "WARNING: mock chỉ kiểm tra pipeline; điểm retrieval không đại diện "
        "chất lượng ngữ nghĩa."
    )

    for query in queries:
        question = str(query["question"])
        metadata_filter = query.get("metadata_filter")
        view = QueryStoreView(store, metadata_filter)
        results = view.search(question, top_k=args.top_k)
        agent = KnowledgeBaseAgent(store=view, llm_fn=demo_llm)

        print(f"\n[{query['id']}] {question}")
        print(f"kind={query['kind']} filter={metadata_filter}")
        print(f"gold_doc_id={query['gold_doc_id']}")
        for rank, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            preview = " ".join(result["content"].split())[:180]
            print(
                f"  {rank}. score={result['score']:.4f} "
                f"doc_id={metadata.get('doc_id', 'unknown')} preview={preview}"
            )
        print(f"agent={agent.answer(question, top_k=args.top_k)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
