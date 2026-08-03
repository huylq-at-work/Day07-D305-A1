from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Tách sau dấu kết câu, giữ lại dấu câu ở cuối mỗi câu.
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if not sentences:
            return []

        size = self.max_sentences_per_chunk
        return [
            " ".join(sentences[start : start + size])
            for start in range(0, len(sentences), size)
        ]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        return self._split(text, self.separators)

    def _hard_split(self, current_text: str) -> list[str]:
        """Cắt cứng theo chunk_size khi không còn dấu phân cách nào dùng được."""
        size = max(1, self.chunk_size)
        return [current_text[i : i + size] for i in range(0, len(current_text), size)]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return self._hard_split(current_text)

        separator, *rest = remaining_separators
        if separator == "":
            return self._hard_split(current_text)

        pieces = current_text.split(separator)
        if len(pieces) == 1:
            # Dấu phân cách này không xuất hiện -> thử dấu ưu tiên kế tiếp.
            return self._split(current_text, rest)

        # Gộp các mảnh liền nhau cho tới sát chunk_size; mảnh nào vẫn quá dài
        # thì đệ quy xuống dấu phân cách mịn hơn.
        chunks: list[str] = []
        buffer = ""
        for piece in pieces:
            candidate = piece if not buffer else buffer + separator + piece
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.append(buffer)
                buffer = ""
            if len(piece) <= self.chunk_size:
                buffer = piece
            else:
                chunks.extend(self._split(piece, rest))
        if buffer:
            chunks.append(buffer)

        return [c for c in chunks if c.strip()]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=max(1, chunk_size // 10)),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison: dict = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            lengths = [len(c) for c in chunks]
            count = len(chunks)
            avg = sum(lengths) / count if count else 0.0
            # Độ lệch chuẩn cho biết chiến lược có sinh ra chunk dài ngắn thất thường
            # hay không — trung bình giống nhau vẫn có thể che một bên toàn mẩu vụn.
            variance = sum((n - avg) ** 2 for n in lengths) / count if count else 0.0
            comparison[name] = {
                "count": count,
                "avg_length": avg,
                "std_length": math.sqrt(variance),
                "min_length": min(lengths) if lengths else 0,
                "max_length": max(lengths) if lengths else 0,
                "chunks": chunks,
            }
        return comparison
