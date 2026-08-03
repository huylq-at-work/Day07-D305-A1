#!/usr/bin/env python3
"""Chạy 5 câu hỏi đánh giá qua KnowledgeBaseAgent và ghi câu trả lời có dẫn nguồn.

    python scripts/answer_demo.py --llm extractive
    python scripts/answer_demo.py --llm demo        # stub do đề cung cấp

PHẦN MỞ RỘNG TỰ THÊM — không nằm trong yêu cầu của đề. Xem đầu file
scripts/extractive_llm.py để biết vì sao và giới hạn của nó.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ingest import build_knowledge_base  # noqa: E402
from src import LocalEmbedder  # noqa: E402
from src.agent import KnowledgeBaseAgent  # noqa: E402
from src.chunking import RecursiveChunker  # noqa: E402


def load_queries(path: Path) -> list[dict]:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))["queries"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", default="extractive", choices=["extractive", "demo"])
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--data-dir", default="data/k3_university")
    parser.add_argument("--queries", default="data/benchmark_queries.yaml")
    parser.add_argument("--out", default="report/benchmark/ANSWERS.md")
    args = parser.parse_args()

    embedder = LocalEmbedder()
    print(f"backend: {embedder._backend_name}")

    store = build_knowledge_base(args.data_dir, embedder,
                                 chunker=RecursiveChunker(chunk_size=args.chunk_size))
    print(f"đã nạp : {store.get_collection_size()} chunk")

    if args.llm == "extractive":
        from scripts.extractive_llm import ExtractiveLLM
        llm_fn = ExtractiveLLM(embedder)
        llm_label = "ExtractiveLLM (tự thêm — trích câu có sẵn, KHÔNG sinh văn bản)"
    else:
        from main import demo_llm
        llm_fn = demo_llm
        llm_label = "demo_llm (stub do đề cung cấp — in lại prompt)"

    agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn)
    queries = load_queries(Path(args.queries))

    lines = [
        "# Câu trả lời của tác tử — 5 câu hỏi đánh giá",
        "",
        "> **PHẦN MỞ RỘNG TỰ THÊM.** Đề bài chỉ yêu cầu `KnowledgeBaseAgent.answer()`",
        "> truy xuất → tạo prompt → gọi `llm_fn`, và cung cấp sẵn `demo_llm` (in lại",
        "> prompt). Repo **không** cấp LLM thật và **không** nói lấy API key ở đâu.",
        "> Nhưng `docs/SCORING.md` lại chấm 2 điểm cho \"câu trả lời của tác tử chính",
        "> xác\" và `docs/EVALUATION.md` bắt xác minh câu trả lời với gold answer —",
        "> điều không làm được với một hàm in lại prompt. Tầng trả lời dưới đây do tôi",
        "> tự thêm để lấp khoảng trống đó, **không phải yêu cầu của đề**.",
        "",
        f"- Tầng trả lời: {llm_label}",
        f"- Embedder: `{embedder._backend_name}`",
        f"- Corpus: `{args.data_dir}` — {store.get_collection_size()} chunk, "
        f"chunker `recursive(chunk_size={args.chunk_size})`, top-k = {args.top_k}",
        "",
        "**Nó KHÔNG sinh ra chữ mới.** Nó chọn những câu có sẵn trong chunk đã truy",
        "xuất, xếp theo độ tương tự với câu hỏi, rồi ghép kèm số nguồn. Gọi đây là",
        "\"câu trả lời do mô hình sinh ra\" là mô tả sai sản phẩm.",
        "",
        "---",
        "",
    ]

    for query in queries:
        answer = agent.answer(query["question"], top_k=args.top_k,
                              metadata_filter=query.get("metadata_filter"))
        print(f"\n=== {query['id']} ===")
        print(answer[:300])

        lines += [
            f"## {query['id']} — `{query['kind']}`",
            "",
            f"**Hỏi:** {query['question']}",
            "",
            f"**Gold answer:** {' '.join(query['gold_answer'].split())}",
            "",
            f"**Bộ lọc:** `{query.get('metadata_filter')}`",
            "",
            "**Tác tử trả lời:**",
            "",
            "```text",
            answer,
            "```",
            "",
        ]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nđã ghi {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
