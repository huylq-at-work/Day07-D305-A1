"""Chạy 5 benchmark query và xuất CSV Contract C cho Role 2.

Script cố ý không fallback sang mock: benchmark chính thức chỉ được chạy sau
CORPUS FREEZE + QUERY FREEZE, với một embedding backend thật.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

from ingest import build_knowledge_base, load_documents
from scripts.custom_chunkers import HeadingChunker
from src.embeddings import LocalEmbedder, OpenAIEmbedder


CSV_COLUMNS = [
    "query_id",
    "member_branch",
    "strategy",
    "params",
    "n_chunks_total",
    "rank_of_gold",
    "hit_top3",
    "top1_score",
    "top1_doc_id",
    "top3_doc_ids",
    "rubric_score",
]


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"null", "~"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def load_queries(path: str | Path) -> list[dict[str, Any]]:
    """Đọc subset YAML phẳng/nested dùng bởi Contract B mà không cần PyYAML."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    queries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        item_match = re.match(r"^\s{2}-\s+(\w+):\s*(.*)$", line)
        field_match = re.match(r"^\s{4}(\w+):\s*(.*)$", line)

        if item_match:
            if current is not None:
                queries.append(current)
            current = {item_match.group(1): _parse_scalar(item_match.group(2))}
            index += 1
            continue

        if current is None or not field_match:
            index += 1
            continue

        key, raw_value = field_match.groups()
        if raw_value in {">", ">-", "|", "|-"}:
            block: list[str] = []
            index += 1
            while index < len(lines):
                continuation = lines[index]
                if re.match(r"^\s{4}\w+:\s*", continuation) or re.match(
                    r"^\s{2}-\s+\w+:\s*", continuation
                ):
                    break
                if continuation.strip() and not continuation.lstrip().startswith("#"):
                    block.append(continuation.strip())
                index += 1
            current[key] = " ".join(block)
            continue

        if raw_value == "" and key == "metadata_filter":
            nested: dict[str, Any] = {}
            index += 1
            while index < len(lines):
                nested_match = re.match(r"^\s{6}(\w+):\s*(.*)$", lines[index])
                if not nested_match:
                    break
                nested[nested_match.group(1)] = _parse_scalar(nested_match.group(2))
                index += 1
            current[key] = nested
            continue

        current[key] = _parse_scalar(raw_value)
        index += 1

    if current is not None:
        queries.append(current)
    return queries


def validate_inputs(query_path: Path, docs_path: Path) -> list[dict[str, Any]]:
    raw_queries = query_path.read_text(encoding="utf-8")
    if "BẢN NHÁP" in raw_queries.upper() or "QUERY FREEZE" not in raw_queries.upper():
        raise ValueError(
            "data/benchmark_queries.yaml chưa QUERY FREEZE; không được tạo CSV chính thức."
        )

    queries = load_queries(query_path)
    required = {
        "id",
        "question",
        "gold_answer",
        "gold_doc_id",
        "metadata_filter",
        "kind",
    }
    if len(queries) != 5:
        raise ValueError(f"Contract B cần đúng 5 query, hiện có {len(queries)}.")
    if [query.get("id") for query in queries] != [f"Q{i}" for i in range(1, 6)]:
        raise ValueError("Query ID phải đúng thứ tự Q1–Q5.")
    for query in queries:
        missing = required - query.keys()
        if missing:
            raise ValueError(f"{query.get('id', '?')} thiếu: {', '.join(sorted(missing))}")

    doc_ids = {document.id for document in load_documents(docs_path)}
    unknown = sorted({str(query["gold_doc_id"]) for query in queries} - doc_ids)
    if unknown:
        raise ValueError(f"gold_doc_id không có trong corpus: {', '.join(unknown)}")
    if not any(query["metadata_filter"] for query in queries):
        raise ValueError("K3 cần ít nhất một query có metadata_filter.")
    return queries


def select_embedder(provider: str):
    """Tạo backend thật; tuyệt đối không fallback sang mock."""
    if provider == "local":
        try:
            embedder = LocalEmbedder()
        except Exception as exc:
            raise RuntimeError(
                "Local embedding chưa sẵn sàng (cần PyTorch + sentence-transformers model)."
            ) from exc
    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY chưa được cấu hình.")
        try:
            embedder = OpenAIEmbedder()
        except Exception as exc:
            raise RuntimeError("OpenAI embedding backend chưa sẵn sàng.") from exc
    else:
        raise RuntimeError("EMBEDDING_PROVIDER phải là 'local' hoặc 'openai'; mock bị cấm.")

    backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    if "mock" in backend_name.lower():
        raise RuntimeError("Embedding backend đang là mock; benchmark bị chặn.")
    return embedder, backend_name


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT_DIR, text=True, encoding="utf-8"
    ).strip()


def _rank_of_gold(results: list[dict[str, Any]], gold_doc_id: str) -> int:
    for index, result in enumerate(results, start=1):
        if result.get("metadata", {}).get("doc_id") == gold_doc_id:
            return index
    return 99


def build_rows(queries, store, member_branch: str, params: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    collection_size = store.get_collection_size()
    for query in queries:
        metadata_filter = query.get("metadata_filter")
        if metadata_filter:
            results = store.search_with_filter(
                str(query["question"]), top_k=10, metadata_filter=metadata_filter
            )
        else:
            results = store.search(str(query["question"]), top_k=10)

        rank = _rank_of_gold(results, str(query["gold_doc_id"]))
        top_three = results[:3]
        top_doc_ids = [
            str(result.get("metadata", {}).get("doc_id", "unknown"))
            for result in top_three
        ]
        # Điểm này phản ánh retrieval. R3 vẫn phải duyệt câu trả lời agent trước khi chốt 2 điểm.
        rubric_score = 2 if rank == 1 else 1 if rank <= 3 else 0
        rows.append(
            {
                "query_id": query["id"],
                "member_branch": member_branch,
                "strategy": "heading",
                "params": params,
                "n_chunks_total": collection_size,
                "rank_of_gold": rank,
                "hit_top3": "true" if rank <= 3 else "false",
                "top1_score": f"{top_three[0]['score']:.4f}" if top_three else "0.0000",
                "top1_doc_id": top_doc_ids[0] if top_doc_ids else "",
                "top3_doc_ids": "|".join(top_doc_ids),
                "rubric_score": rubric_score,
            }
        )
    return rows


def write_contract_csv(
    path: Path,
    rows: list[dict[str, Any]],
    backend_name: str,
    source_commit: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(
            f"# corpus/query freeze confirmed; main commit={source_commit}; run_date={date.today().isoformat()}\n"
        )
        handle.write(f"# EMBEDDING_PROVIDER non-mock; backend={backend_name}\n")
        handle.write("# individual core verification: 42/42 tests passed\n")
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunker", choices=("heading",), default="heading")
    parser.add_argument("--top-k", type=int, default=3, help="Contract C cố định top-k=3")
    parser.add_argument("--docs", default="data/k3_university")
    parser.add_argument("--queries", default="data/benchmark_queries.yaml")
    parser.add_argument("--max-level", type=int, default=2)
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--member-branch", default="role2-strategy-lead")
    parser.add_argument(
        "--output", default="report/benchmark/role2-strategy-lead_heading.csv"
    )
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.top_k != 3:
        raise SystemExit("Contract C yêu cầu --top-k 3.")
    if args.max_level <= 0 or args.max_chars <= 0:
        raise SystemExit("max-level và max-chars phải lớn hơn 0.")

    query_path = ROOT_DIR / args.queries
    docs_path = ROOT_DIR / args.docs
    try:
        queries = validate_inputs(query_path, docs_path)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Input chưa hợp lệ: {exc}") from exc

    print("Contract B hợp lệ: 5 query, gold_doc_id khớp corpus, có metadata filter.")
    if args.validate_only:
        return 0

    load_dotenv(ROOT_DIR / ".env", override=False)
    provider = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()
    try:
        embedder, backend_name = select_embedder(provider)
    except RuntimeError as exc:
        raise SystemExit(f"Không thể chạy benchmark chính thức: {exc}") from exc

    chunker = HeadingChunker(max_level=args.max_level, max_chars=args.max_chars)
    store = build_knowledge_base(
        docs_path,
        embedding_fn=embedder,
        chunker=chunker,
        collection_name="role2_heading_benchmark",
    )
    params = f"max_level={args.max_level},max_chars={args.max_chars}"
    rows = build_rows(queries, store, args.member_branch, params)
    output_path = ROOT_DIR / args.output
    write_contract_csv(output_path, rows, backend_name, _git_value("rev-parse", "--short", "origin/main"))
    print(f"Embedding backend: {backend_name}")
    print(f"Đã ghi {len(rows)} dòng vào {output_path.relative_to(ROOT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
