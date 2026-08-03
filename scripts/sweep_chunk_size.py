#!/usr/bin/env python3
"""Quét `chunk_size` cho RecursiveChunker trên đúng 5 câu hỏi đánh giá.

    python scripts/sweep_chunk_size.py --sizes 300 500 800

Đo HAI chỉ số cho mỗi câu hỏi, vì chúng nói hai chuyện khác nhau:

  rank_doc    hạng của tài liệu gold — đúng chỉ số rubric chấm, nhưng hỏng khi
              `gold_doc_id` khai thiếu (Q3, Q5 có đáp án ở nhiều tài liệu).
  rank_needle hạng của chunk THỰC SỰ chứa câu trả lời, dò bằng một chuỗi mốc.
              Không phụ thuộc nhãn, nên dùng để so các chunk_size với nhau.

`rank_needle = -1` nghĩa là KHÔNG chunk nào chứa trọn chuỗi mốc — ranh giới cắt
đã xẻ đôi câu trả lời. Đó là kết quả đáng giá, không phải lỗi chạy.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ingest import build_knowledge_base  # noqa: E402
from src import LocalEmbedder  # noqa: E402
from src.chunking import RecursiveChunker, compute_similarity  # noqa: E402

# Chuỗi chắc chắn nằm trong đoạn văn chứa câu trả lời của từng câu hỏi.
NEEDLES = {
    "Q1": "18-22 credits",
    "Q2": "30% of the study time",
    "Q3": "50% of the total credits",
    "Q4": "hủy học phần chưa đóng học phí",
    "Q5": "one week before the start of the new semester",
}


def matches(metadata: dict, metadata_filter: dict | None) -> bool:
    if not metadata_filter:
        return True
    return all(str(metadata.get(k)) == str(v) for k, v in metadata_filter.items())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=int, nargs="+", default=[300, 500, 800])
    parser.add_argument("--data-dir", default="data/k3_university")
    parser.add_argument("--queries", default="data/benchmark_queries.yaml")
    parser.add_argument("--out", default="report/strategy/chunk_size_sweep.json")
    args = parser.parse_args()

    import yaml
    queries = yaml.safe_load(Path(args.queries).read_text(encoding="utf-8"))["queries"]

    embedder = LocalEmbedder()
    print(f"backend: {embedder._backend_name}\n")

    results = {}
    for size in args.sizes:
        store = build_knowledge_base(args.data_dir, embedder,
                                     chunker=RecursiveChunker(chunk_size=size))
        records = store._store
        lengths = [len(r["content"]) for r in records]
        avg = sum(lengths) / len(lengths)

        print(f"=== chunk_size={size} — {len(records)} chunk, dài TB {avg:.1f} ===")
        header = f"{'#':<4}{'rank_doc':>10}{'rank_needle':>13}{'pool':>7}{'top1':>9}"
        print(header)
        print("-" * len(header))

        rows = []
        for query in queries:
            flt = query.get("metadata_filter")
            pool = [r for r in records if matches(r["metadata"], flt)]
            hits = store.search_with_filter(query["question"], top_k=10, metadata_filter=flt)

            rank_doc = next(
                (i for i, h in enumerate(hits, 1)
                 if h["metadata"].get("doc_id") == query["gold_doc_id"]), 99
            )

            needle = NEEDLES[query["id"]].lower()
            target = next((r for r in pool if needle in r["content"].lower()), None)
            if target is None:
                rank_needle, needle_score = -1, None
            else:
                q_vec = embedder(query["question"])
                needle_score = compute_similarity(q_vec, target["embedding"])
                rank_needle = 1 + sum(
                    1 for r in pool
                    if compute_similarity(q_vec, r["embedding"]) > needle_score
                )

            top1 = hits[0]["score"] if hits else 0.0
            shown = "CẮT ĐÔI" if rank_needle == -1 else str(rank_needle)
            print(f"{query['id']:<4}{rank_doc:>10}{shown:>13}{len(pool):>7}{top1:>9.4f}")

            rows.append({
                "query_id": query["id"], "rank_doc": rank_doc,
                "rank_needle": rank_needle,
                "needle_score": round(needle_score, 4) if needle_score else None,
                "pool_size": len(pool), "top1_score": round(top1, 4),
                "rubric": 2 if rank_doc == 1 else (1 if rank_doc <= 3 else 0),
            })

        total = sum(r["rubric"] for r in rows)
        found = [r["rank_needle"] for r in rows if r["rank_needle"] > 0]
        print(f"điểm rubric: {total}/10 | rank_needle trung bình: "
              f"{sum(found)/len(found):.1f} ({len(found)}/5 câu tìm được mốc)\n")

        results[size] = {
            "n_chunks": len(records), "avg_length": round(avg, 1),
            "rubric_total": total, "rows": rows,
        }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"đã ghi {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
