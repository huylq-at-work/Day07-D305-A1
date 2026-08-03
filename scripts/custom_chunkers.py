"""Các chiến lược chunking tùy chỉnh do Role 2 sở hữu."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.chunking import RecursiveChunker


class HeadingChunker:
    """Chia quy định học vụ theo heading/mục và giữ heading trong mọi chunk.

    Markdown heading được nhận diện tới ``max_level``. Vì corpus K3 chứa nhiều
    văn bản được trích từ HTML/PDF, class cũng nhận diện các dòng pháp quy như
    ``Chương I``, ``Điều 5``, ``Chapter II`` và ``Article 7``.
    """

    MIN_SECTION_CHARS = 80
    _LEGAL_HEADING_RE = re.compile(
        r"^(?:chương|điều|phần|mục|chapter|article|part|section)\s+"
        r"(?:[ivxlcdm]+|\d+(?:\.\d+)*[a-z]?)"
        r"(?:\s*[.):\-–—]|\s+|$).*",
        re.IGNORECASE,
    )

    def __init__(self, max_level: int = 2, max_chars: int = 1200) -> None:
        self.max_level = max(1, max_level)
        self.max_chars = max(1, max_chars)

    def _is_heading(self, line: str) -> bool:
        stripped = line.strip()
        markdown = re.match(r"^(#{1,6})\s+\S", stripped)
        if markdown:
            return len(markdown.group(1)) <= self.max_level
        return bool(self._LEGAL_HEADING_RE.match(stripped))

    def _collect_sections(self, text: str) -> list[str]:
        """Tách section nhưng vẫn giữ phần mở đầu trước heading đầu tiên."""
        sections: list[str] = []
        current: list[str] = []

        for line in text.splitlines():
            if self._is_heading(line) and current:
                section = "\n".join(current).strip()
                if section:
                    sections.append(section)
                current = [line.strip()]
            else:
                current.append(line)

        final_section = "\n".join(current).strip()
        if final_section:
            sections.append(final_section)
        return sections

    def _merge_short_sections(self, sections: list[str]) -> list[str]:
        """Gộp section quá ngắn về phía section kế tiếp để tránh chunk vụn."""
        merged: list[str] = []
        index = 0
        while index < len(sections):
            section = sections[index]
            first_line = section.splitlines()[0] if section.splitlines() else ""
            is_short_heading = (
                self._is_heading(first_line)
                and len(section) < self.MIN_SECTION_CHARS
                and index + 1 < len(sections)
            )
            if is_short_heading:
                merged.append(f"{section}\n\n{sections[index + 1]}")
                index += 2
            else:
                merged.append(section)
                index += 1
        return merged

    def _split_long_section(self, section: str) -> list[str]:
        if len(section) <= self.max_chars:
            return [section]

        lines = section.splitlines()
        heading = lines[0].strip() if lines and self._is_heading(lines[0]) else ""
        body = "\n".join(lines[1:] if heading else lines).strip()

        if not heading:
            return RecursiveChunker(chunk_size=self.max_chars).chunk(body)

        body_limit = max(1, self.max_chars - len(heading) - 2)
        body_chunks = RecursiveChunker(chunk_size=body_limit).chunk(body)
        if not body_chunks:
            return [heading]
        return [f"{heading}\n\n{piece}".strip() for piece in body_chunks]

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = self._collect_sections(text.strip())
        sections = self._merge_short_sections(sections)

        chunks: list[str] = []
        for section in sections:
            chunks.extend(self._split_long_section(section))
        return [chunk for chunk in chunks if chunk.strip()]


__all__ = ["HeadingChunker"]
