"""Benchmark cá nhân Role 2 trên đúng 5 query chung của nhóm.

Pipeline giữ nguyên dữ liệu, query và embedding; biến chiến lược duy nhất là
HeadingChunker. Benchmark yêu cầu ``EMBEDDING_PROVIDER=local`` và không fallback
sang mock để số liệu phản ánh ngữ nghĩa.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

from ingest import build_knowledge_base
from main import demo_llm
from scripts.custom_chunkers import HeadingChunker
from scripts.run_benchmark import load_queries
from src import KnowledgeBaseAgent, LocalEmbedder


# Mỗi tuple là một điều kiện; ít nhất một chuỗi trong tuple phải có mặt trong
# context top-3. Các chuỗi này được trích nguyên văn từ gold answer/corpus.
ANSWER_MARKERS = {
    "Q1": [("18-22 credits", "18–22 credits")],
    "Q2": [("30%",), ("maximum of 18 credits",)],
    "Q3": [("50%",), ("during the first week of the semester",)],
    "Q4": [("hủy học phần chưa đóng học phí",)],
    "Q5": [("at least one month before",), ("at least one week before",)],
}


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


def evaluate_answer_evidence(query_id: str, results: list[dict[str, Any]]) -> tuple[bool, list[bool]]:
    """Kiểm tra top-3 có chứa các chuỗi bằng chứng của gold answer hay không."""
    context = "\n".join(result["content"] for result in results).lower()
    checks = [
        any(marker.lower() in context for marker in alternatives)
        for alternatives in ANSWER_MARKERS[query_id]
    ]
    return all(checks), checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", default="data/k3_university")
    parser.add_argument("--queries", default="data/benchmark_queries.yaml")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--max-level", type=int, default=2)
    parser.add_argument("--max-chars", type=int, default=1200)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    if args.top_k <= 0 or args.max_level <= 0 or args.max_chars <= 0:
        raise SystemExit("top-k, max-level và max-chars phải lớn hơn 0.")

    queries = load_queries(args.queries)
    if len(queries) != 5:
        raise SystemExit(f"Benchmark cần đúng 5 query, hiện có {len(queries)}.")

    load_dotenv(override=False)
    provider = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()
    if provider != "local":
        raise SystemExit("Benchmark yêu cầu EMBEDDING_PROVIDER=local trong .env.")

    try:
        embedding_fn = LocalEmbedder()
    except Exception as exc:
        raise SystemExit(f"Không khởi tạo được local embedding: {exc}") from exc
    backend_name = getattr(embedding_fn, "_backend_name", embedding_fn.__class__.__name__)
    if "mock" in backend_name.lower():
        raise SystemExit("Local embedding đã fallback sang mock; dừng benchmark.")

    chunker = HeadingChunker(max_level=args.max_level, max_chars=args.max_chars)
    store = build_knowledge_base(
        args.docs,
        embedding_fn=embedding_fn,
        chunker=chunker,
        collection_name="role2_personal_heading",
    )

    print("=== BENCHMARK CÁ NHÂN — ROLE 2 ===")
    print("strategy=heading")
    print(f"params=max_level={args.max_level},max_chars={args.max_chars}")
    print(f"embedding_backend={backend_name}")
    print(f"n_chunks_total={store.get_collection_size()}")

    for query in queries:
        question = str(query["question"])
        metadata_filter = query.get("metadata_filter")
        view = QueryStoreView(store, metadata_filter)
        results = view.search(question, top_k=args.top_k)
        agent = KnowledgeBaseAgent(store=view, llm_fn=demo_llm)
        has_answer, marker_checks = evaluate_answer_evidence(str(query["id"]), results)

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
        print(f"answer_markers={marker_checks} relevant_chunk_in_top3={has_answer}")
        if metadata_filter:
            unfiltered = store.search(question, top_k=args.top_k)
            filtered_ids = [result["metadata"].get("doc_id") for result in results]
            unfiltered_ids = [result["metadata"].get("doc_id") for result in unfiltered]
            print(f"A/B filtered_top3={filtered_ids}")
            print(f"A/B unfiltered_top3={unfiltered_ids}")
            print(f"A/B filter_changed_ranking={filtered_ids != unfiltered_ids}")
        print(f"agent={agent.answer(question, top_k=args.top_k)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
