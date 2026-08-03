#!/usr/bin/env python3
"""Chạy 5 câu hỏi đánh giá và xuất CSV theo docs/CONTRACTS.md §3 (Contract C).

    python scripts/run_benchmark.py --chunker recursive --top-k 3

Mỗi thành viên chạy cùng bộ câu hỏi trên CHIẾN LƯỢC CHUNKING RIÊNG của mình.
Bốn file CSV cùng 11 cột được `scripts/merge_benchmark.py` gộp thành ALL.csv —
đó là nguồn duy nhất cho mọi bảng trong REPORT_NHOM.md.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ingest import build_knowledge_base  # noqa: E402
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker  # noqa: E402

# Sâu hơn top_k: cần biết chunk đúng đứng hạng mấy kể cả khi nó trượt top-3.
RANK_SEARCH_DEPTH = 10
RANK_NOT_FOUND = 99

FIELDS = [
    "query_id", "member_branch", "strategy", "params", "n_chunks_total",
    "rank_of_gold", "hit_top3", "top1_score", "top1_doc_id", "top3_doc_ids",
    "rubric_score",
]


def build_chunker(name: str, chunk_size: int, overlap: int, max_sentences: int):
    """Trả về (chunker, chuỗi mô tả tham số) cho cột `params` của Contract C."""
    if name == "fixed":
        return FixedSizeChunker(chunk_size=chunk_size, overlap=overlap), \
            f"chunk_size={chunk_size},overlap={overlap}"
    if name == "sentence":
        return SentenceChunker(max_sentences_per_chunk=max_sentences), \
            f"max_sentences_per_chunk={max_sentences}"
    if name == "recursive":
        return RecursiveChunker(chunk_size=chunk_size), f"chunk_size={chunk_size}"
    if name == "heading":
        try:
            from scripts.custom_chunkers import HeadingChunker
        except ImportError:
            raise SystemExit(
                "Chưa có scripts/custom_chunkers.py (HeadingChunker là phần của R2)."
            )
        return HeadingChunker(), "level=2"
    raise SystemExit(f"Chiến lược không hợp lệ: {name}")


def select_embedder(provider: str):
    """Chọn embedder và TRẢ VỀ CẢ TÊN BACKEND để người chạy tự kiểm."""
    if provider == "mock":
        from src.embeddings import _mock_embed
        return _mock_embed, _mock_embed._backend_name
    from src import LocalEmbedder
    embedder = LocalEmbedder()
    return embedder, embedder._backend_name


def load_queries(path: Path) -> list[dict]:
    try:
        import yaml
    except ImportError:
        raise SystemExit("Cần pyyaml để đọc benchmark_queries.yaml: pip install pyyaml")
    queries = yaml.safe_load(path.read_text(encoding="utf-8"))["queries"]
    if len(queries) != 5:
        raise SystemExit(f"Contract B yêu cầu đúng 5 câu hỏi, file có {len(queries)}.")
    return queries


def rank_of_gold(hits: list[dict], gold_doc_id: str) -> int:
    """Vị trí (1-based) của chunk đầu tiên thuộc tài liệu gold; 99 nếu ngoài top-10."""
    for position, hit in enumerate(hits, start=1):
        if hit["metadata"].get("doc_id") == gold_doc_id:
            return position
    return RANK_NOT_FOUND


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chunker", required=True,
                        choices=["fixed", "sentence", "recursive", "heading"])
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    parser.add_argument("--max-sentences", type=int, default=3)
    parser.add_argument("--data-dir", default="data/k3_university")
    parser.add_argument("--queries", default="data/benchmark_queries.yaml")
    parser.add_argument("--branch", default=None, help="mặc định: lấy từ git")
    parser.add_argument("--provider", default="local", choices=["local", "mock"],
                        help="mock CHỈ để thử nhanh; số liệu từ mock không dùng làm bằng chứng")
    parser.add_argument("--out-dir", default="report/benchmark")
    args = parser.parse_args()

    branch = args.branch
    if not branch:
        import subprocess
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True, cwd=REPO_ROOT
                                ).stdout.strip() or "unknown"

    embedder, backend = select_embedder(args.provider)
    print(f"backend      : {backend}")
    if "mock" in backend.lower() and args.provider != "mock":
        raise SystemExit(
            "DỪNG: LocalEmbedder đã âm thầm rơi về mock. Mock cho điểm gần như ngẫu "
            "nhiên — kết luận rút ra từ nó là kết luận từ nhiễu. Xem README mục "
            "'Tùy Chọn Mô Hình Nhúng'."
        )

    chunker, params = build_chunker(args.chunker, args.chunk_size, args.overlap,
                                    args.max_sentences)
    store = build_knowledge_base(args.data_dir, embedder, chunker=chunker)
    total_chunks = store.get_collection_size()
    doc_ids = {r["metadata"].get("doc_id") for r in store._store}
    print(f"chiến lược   : {args.chunker} ({params})")
    print(f"corpus       : {args.data_dir}")
    print(f"đã nạp       : {total_chunks} chunk từ {len(doc_ids)} tài liệu")

    if total_chunks == 0:
        raise SystemExit("DỪNG: store rỗng — kiểm lại --data-dir và front matter.")

    queries = load_queries(Path(args.queries))
    rows = []

    print(f"\n{'#':<4}{'rank':>6}{'top1':>9}  {'lọc':<8}{'tài liệu hạng 1'}")
    print("-" * 74)

    for query in queries:
        gold = query["gold_doc_id"]
        metadata_filter = query.get("metadata_filter")

        deep = store.search_with_filter(query["question"], top_k=RANK_SEARCH_DEPTH,
                                        metadata_filter=metadata_filter)
        hits = deep[: args.top_k]
        rank = rank_of_gold(deep, gold)

        # Chấm phần TRUY XUẤT theo docs/SCORING.md. Điểm 2 còn phụ thuộc câu trả
        # lời của agent — người chạy tự hạ xuống 1 nếu câu trả lời thiếu chi tiết.
        retrieval_score = 2 if rank == 1 else (1 if rank <= 3 else 0)

        rows.append({
            "query_id": query["id"],
            "member_branch": branch,
            "strategy": args.chunker,
            "params": params,
            "n_chunks_total": total_chunks,
            "rank_of_gold": rank,
            "hit_top3": str(rank <= 3).lower(),
            "top1_score": f"{hits[0]['score']:.4f}" if hits else "0.0000",
            "top1_doc_id": hits[0]["metadata"].get("doc_id", "") if hits else "",
            "top3_doc_ids": "|".join(h["metadata"].get("doc_id", "") for h in hits[:3]),
            "rubric_score": retrieval_score,
        })

        flag = "có" if metadata_filter else "-"
        top1 = rows[-1]["top1_doc_id"]
        mark = "" if rank == 1 else ("  <- gold hạng %d" % rank if rank <= 3 else "  <- TRƯỢT")
        print(f"{query['id']:<4}{rank:>6}{rows[-1]['top1_score']:>9}  {flag:<8}{top1}{mark}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{branch}_{args.chunker}.csv"
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        # Ba dòng điều kiện hợp lệ theo Contract C — không có chúng thì người đọc
        # không biết số này chạy bằng embedder nào, trên corpus nào.
        handle.write(f"# backend={backend}\n")
        handle.write(f"# corpus={args.data_dir} chunks={total_chunks} docs={len(doc_ids)}\n")
        handle.write(f"# queries={args.queries} top_k={args.top_k} branch={branch}\n")
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    total = sum(r["rubric_score"] for r in rows)
    hits3 = sum(1 for r in rows if r["hit_top3"] == "true")
    print(f"\ntop-3 trúng  : {hits3}/5")
    print(f"điểm truy xuất: {total}/10  (chưa trừ theo chất lượng câu trả lời)")
    print(f"đã ghi       : {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
