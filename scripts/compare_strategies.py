"""Xuất baseline Contract D và bảng so sánh HeadingChunker của Role 2."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ingest import load_documents
from scripts.custom_chunkers import HeadingChunker
from src import ChunkingStrategyComparator, LocalEmbedder

PREFERRED_DOC_IDS = (
    "ou-quy-che-hoc-vu-tin-chi",
    "vinuni-academic-regulations-undergrad",
    "vinuni-credit-transfer",
)


def _stats(chunks: list[str]) -> dict[str, float | int]:
    lengths = [len(chunk) for chunk in chunks]
    count = len(lengths)
    average = sum(lengths) / count if count else 0.0
    variance = sum((length - average) ** 2 for length in lengths) / count if count else 0.0
    return {
        "count": count,
        "avg_length": average,
        "std_length": math.sqrt(variance),
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
    }


def _select_documents(documents, limit: int, requested_ids: list[str] | None):
    by_id = {document.id: document for document in documents}
    if requested_ids:
        missing = [doc_id for doc_id in requested_ids if doc_id not in by_id]
        if missing:
            raise ValueError(f"Không tìm thấy doc_id: {', '.join(missing)}")
        return [by_id[doc_id] for doc_id in requested_ids[:limit]]

    preferred = [by_id[doc_id] for doc_id in PREFERRED_DOC_IDS if doc_id in by_id]
    if len(preferred) >= limit:
        return preferred[:limit]

    selected = list(preferred)
    for document in documents:
        if document.id not in {item.id for item in selected}:
            selected.append(document)
        if len(selected) == limit:
            break
    return selected


def _find_boundary_example(text: str, fixed_chunks: list[str], heading_chunks: list[str]) -> dict[str, str]:
    if len(fixed_chunks) < 2:
        return {
            "fixed_boundary": "Không có đủ hai fixed-size chunk để minh họa.",
            "heading_chunk": heading_chunks[0][:500] if heading_chunks else "Không có chunk.",
        }

    first_size = len(fixed_chunks[0])
    overlap = min(50, max(0, first_size - 1))
    step = max(1, first_size - overlap)

    for start in range(0, max(0, len(text) - first_size), step):
        boundary = start + first_size
        if boundary >= len(text) or not (text[boundary - 1].isalnum() and text[boundary].isalnum()):
            continue
        needle = text[max(0, boundary - 30) : min(len(text), boundary + 30)]
        for heading_chunk in heading_chunks:
            if needle in heading_chunk:
                return {
                    "fixed_boundary": text[max(0, boundary - 120) : min(len(text), boundary + 120)].strip(),
                    "heading_chunk": heading_chunk[:800].strip(),
                }

    for fixed_chunk in fixed_chunks[:-1]:
        if fixed_chunk and fixed_chunk[-1].isalnum():
            return {
                "fixed_boundary": fixed_chunk[-240:].strip(),
                "heading_chunk": heading_chunks[0][:800].strip() if heading_chunks else "Không có chunk.",
            }
    return {
        "fixed_boundary": fixed_chunks[0][-240:].strip(),
        "heading_chunk": heading_chunks[0][:800].strip() if heading_chunks else "Không có chunk.",
    }


def _json_dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# So sánh baseline và HeadingChunker — Role 2",
        "",
        f"- Embedding backend đã xác nhận: `{payload['embedding_backend']}`",
        f"- Tham số baseline: `chunk_size={payload['chunk_size']}`",
        (
            "- Tham số HeadingChunker: "
            f"`max_level={payload['heading_params']['max_level']}, "
            f"max_chars={payload['heading_params']['max_chars']}, "
            f"min_section_chars={payload['heading_params']['min_section_chars']}`"
        ),
        "",
        "## Bảng kết quả",
        "",
        "| Tài liệu | Chiến lược | Số chunk | Dài TB | Độ lệch | Min | Max |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for document in payload["documents"]:
        for strategy, stats in document["strategies"].items():
            lines.append(
                f"| {document['doc_id']} | {strategy} | {stats['count']} | "
                f"{stats['avg_length']:.2f} | {stats['std_length']:.2f} | "
                f"{stats['min_length']} | {stats['max_length']} |"
            )

    example = payload["documents"][0]["cut_example"]
    lines.extend(
        [
            "",
            "## Ví dụ fixed-size cắt hỏng, heading giữ nguyên",
            "",
            f"Tài liệu: `{payload['documents'][0]['doc_id']}`.",
            "",
            "**Ngữ cảnh quanh ranh giới fixed-size:**",
            "",
            "> " + example["fixed_boundary"].replace("\n", " "),
            "",
            "**Chunk theo heading chứa trọn ngữ cảnh:**",
            "",
            "> " + example["heading_chunk"].replace("\n", " "),
            "",
            "## Nhận xét",
            "",
            "- Fixed-size giữ độ dài đều nhưng có thể cắt giữa từ, câu hoặc điều khoản.",
            "- Sentence chunking tránh cắt giữa câu nhưng độ dài dao động khi câu nguồn quá dài.",
            "- Recursive chunking khống chế kích thước tốt hơn nhưng không luôn giữ tên điều khoản.",
            "- HeadingChunker giữ tiêu đề trên từng mảnh con, giúp chunk đứng độc lập vẫn còn ngữ cảnh pháp quy.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", default="data/k3_university", help="Thư mục corpus K3")
    parser.add_argument("--limit", type=int, choices=(2, 3), default=3)
    parser.add_argument("--chunk-size", type=int, default=200)
    parser.add_argument("--doc-id", action="append", dest="doc_ids")
    parser.add_argument("--output-dir", default="report/strategy")
    parser.add_argument("--heading-max-level", type=int, default=2)
    parser.add_argument("--heading-max-chars", type=int, default=1200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.chunk_size <= 0 or args.heading_max_chars <= 0:
        raise SystemExit("chunk-size và heading-max-chars phải lớn hơn 0")

    try:
        embedder = LocalEmbedder()
    except Exception as exc:
        raise SystemExit(
            "Local embedding chưa sẵn sàng. Chạy "
            "`python -m pip install -r requirements-local.txt` rồi thử lại. "
            f"Chi tiết: {exc}"
        ) from exc

    backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    if "mock" in backend_name.lower():
        raise SystemExit("Baseline không hợp lệ vì embedding backend đang là mock.")

    documents = load_documents(args.docs)
    selected = _select_documents(documents, args.limit, args.doc_ids)
    if len(selected) < 2:
        raise SystemExit("Cần ít nhất 2 tài liệu để so sánh chiến lược.")

    output_dir = Path(args.output_dir)
    comparator = ChunkingStrategyComparator()
    heading_chunker = HeadingChunker(
        max_level=args.heading_max_level,
        max_chars=args.heading_max_chars,
    )
    summary: dict[str, Any] = {
        "embedding_backend": backend_name,
        "chunk_size": args.chunk_size,
        "heading_params": {
            "max_level": heading_chunker.max_level,
            "max_chars": heading_chunker.max_chars,
            "min_section_chars": heading_chunker.MIN_SECTION_CHARS,
        },
        "documents": [],
    }

    for document in selected:
        comparison = comparator.compare(document.content, chunk_size=args.chunk_size)
        baseline_payload = {
            "doc_id": document.id,
            "chunk_size": args.chunk_size,
            "embedding_backend": backend_name,
            "comparison": comparison,
        }
        _json_dump(output_dir / f"baseline_{document.id}.json", baseline_payload)

        heading_chunks = heading_chunker.chunk(document.content)
        strategy_stats = {
            name: _stats(result["chunks"])
            for name, result in comparison.items()
        }
        strategy_stats["heading"] = _stats(heading_chunks)
        summary["documents"].append(
            {
                "doc_id": document.id,
                "char_count": len(document.content),
                "strategies": strategy_stats,
                "cut_example": _find_boundary_example(
                    document.content,
                    comparison["fixed_size"]["chunks"],
                    heading_chunks,
                ),
            }
        )

    _json_dump(output_dir / "heading_comparison.json", summary)
    (output_dir / "HEADING_COMPARISON.md").write_text(
        _render_markdown(summary),
        encoding="utf-8",
    )

    print(f"Embedding backend: {backend_name}")
    print("Đã xuất baseline cho:", ", ".join(document.id for document in selected))
    print(f"Bảng so sánh: {output_dir / 'HEADING_COMPARISON.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
