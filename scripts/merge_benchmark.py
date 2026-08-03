#!/usr/bin/env python3
"""Gộp CSV benchmark của cả nhóm thành ALL.csv — docs/CONTRACTS.md §5.

    python scripts/merge_benchmark.py report/benchmark/ --output report/benchmark/ALL.csv

Script **báo lỗi thay vì bỏ qua** dòng hỏng. Một dòng sai định dạng làm sai cả
bốn bảng dẫn xuất trong REPORT_NHOM cùng lúc, và sai lặng lẽ — người đọc báo
cáo không có cách nào nhìn ra.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

COLUMNS = [
    "query_id", "member_branch", "strategy", "params", "n_chunks_total",
    "rank_of_gold", "hit_top3", "top1_score", "top1_doc_id", "top3_doc_ids",
    "rubric_score",
]
VALID_QUERY_IDS = {"Q1", "Q2", "Q3", "Q4", "Q5"}
VALID_STRATEGIES = {"fixed", "sentence", "recursive", "heading"}


def read_rows(path: Path, problems: list[str]) -> list[dict]:
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if not l.startswith("#")]
    reader = csv.DictReader(lines)

    if reader.fieldnames != COLUMNS:
        problems.append(
            f"{path.name}: sai header.\n"
            f"    cần : {COLUMNS}\n"
            f"    thấy: {reader.fieldnames}"
        )
        return []

    rows = list(reader)
    if len(rows) != 5:
        problems.append(f"{path.name}: cần đúng 5 dòng (Q1–Q5), thấy {len(rows)}")

    ids = [r["query_id"] for r in rows]
    if set(ids) - VALID_QUERY_IDS:
        problems.append(f"{path.name}: query_id lạ {sorted(set(ids) - VALID_QUERY_IDS)}")

    for row in rows:
        if row["strategy"] not in VALID_STRATEGIES:
            problems.append(f"{path.name} {row['query_id']}: strategy lạ {row['strategy']!r}")
        try:
            int(row["rank_of_gold"]), int(row["n_chunks_total"]), int(row["rubric_score"])
            float(row["top1_score"])
        except ValueError as error:
            problems.append(f"{path.name} {row['query_id']}: kiểu dữ liệu sai ({error})")

    # n_chunks_total phải giống nhau ở cả 5 dòng: khác nhau nghĩa là người đó
    # nạp lại corpus giữa chừng, và số liệu không dùng làm bằng chứng được.
    sizes = {r["n_chunks_total"] for r in rows}
    if len(sizes) > 1:
        problems.append(
            f"{path.name}: n_chunks_total không nhất quán {sorted(sizes)} "
            "— corpus bị nạp lại giữa chừng?"
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, default=Path("report/benchmark/ALL.csv"))
    args = parser.parse_args()

    files = sorted(
        p for p in args.directory.glob("*.csv")
        if p.name != args.output.name and "_v1-" not in p.name
    )
    if not files:
        raise SystemExit(f"Không tìm thấy CSV nào trong {args.directory}")

    problems: list[str] = []
    all_rows: list[dict] = []
    for path in files:
        rows = read_rows(path, problems)
        all_rows.extend(rows)
        print(f"đọc {path.name:44} {len(rows)} dòng")

    if problems:
        print("\nDỪNG — có lỗi định dạng, không ghi ALL.csv:", file=sys.stderr)
        for problem in problems:
            print(f"  ! {problem}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    # Gộp theo (thành viên, chiến lược): một người có thể chạy nhiều cấu hình,
    # cộng dồn theo tên người thôi sẽ ra điểm quá 10 và vô nghĩa.
    by_run: dict[tuple[str, str], int] = defaultdict(int)
    chunks: dict[tuple[str, str], str] = {}
    for row in all_rows:
        key = (row["member_branch"], row["strategy"])
        by_run[key] += int(row["rubric_score"])
        chunks[key] = row["n_chunks_total"]

    print(f"\n{len(all_rows)} dòng ({len(by_run)} lần chạy) -> {args.output}\n")
    print(f"{'thành viên':32}{'chiến lược':12}{'chunk':>7}{'điểm':>8}")
    print("-" * 59)
    for key in sorted(by_run, key=lambda k: (-by_run[k], k[0])):
        print(f"{key[0]:32}{key[1]:12}{chunks[key]:>7}{by_run[key]:>6}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
