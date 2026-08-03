#!/usr/bin/env python3
"""`llm_fn` trích xuất — trả lời có dẫn nguồn mà KHÔNG cần LLM hay API key.

ĐÂY KHÔNG PHẢI LLM. Nó không sinh ra chữ mới: nó chọn những CÂU CÓ SẴN trong các
chunk đã truy xuất, xếp theo độ tương tự với câu hỏi, rồi ghép lại kèm số nguồn.
Phải nói rõ điều này trong báo cáo — gọi nó là "câu trả lời do mô hình sinh ra"
là mô tả sai sản phẩm.

Vì sao vẫn đáng làm: nó biến `KnowledgeBaseAgent` từ "code xong nhưng chưa chạy
thật" thành một tầng trả lời **kiểm chứng được** — mỗi câu trong câu trả lời truy
ngược được về đúng chunk nào, đúng tài liệu nào. Đó chính là thứ tiêu chí
*Grounding Quality* trong docs/EVALUATION.md yêu cầu chỉ ra.

Đánh đổi phải chấp nhận: nó không diễn giải, không tổng hợp hai nguồn thành một
câu, không trả lời được câu hỏi cần suy luận. Nếu câu trả lời nằm rải ở hai mệnh
đề cách xa nhau thì nó chỉ lấy được một.

    from scripts.extractive_llm import ExtractiveLLM
    agent = KnowledgeBaseAgent(store=store, llm_fn=ExtractiveLLM(embedder))
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chunking import compute_similarity  # noqa: E402

# Khớp dòng tiêu đề nguồn do KnowledgeBaseAgent.answer() sinh ra.
SOURCE_HEADER = re.compile(r"^\[(\d+)\] \(nguồn: (.+?), score=([\d.\-]+)\)$", re.M)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?;:])\s+|\n")


class ExtractiveLLM:
    """Chọn câu liên quan nhất trong ngữ cảnh, ghép lại kèm trích dẫn [n]."""

    def __init__(
        self,
        embedder,
        max_sentences: int = 3,
        min_score: float = 0.35,
        min_sentence_chars: int = 30,
    ) -> None:
        self.embedder = embedder
        self.max_sentences = max_sentences
        # Dưới ngưỡng này thì thà nói "không đủ thông tin" còn hơn đưa ra một câu
        # trông giống câu trả lời. Ngưỡng lấy từ thí nghiệm ở Bài tập 3.3: cặp câu
        # hoàn toàn không liên quan cho ~0.07, cặp cùng miền cho ~0.52.
        self.min_score = min_score
        self.min_sentence_chars = min_sentence_chars

    def _parse_context(self, prompt: str) -> list[tuple[int, str, str]]:
        """Tách prompt ngược thành [(số nguồn, doc_id, nội dung chunk)]."""
        matches = list(SOURCE_HEADER.finditer(prompt))
        if not matches:
            return []

        end_of_context = prompt.find("\nCÂU HỎI:")
        blocks = []
        for position, match in enumerate(matches):
            start = match.end()
            stop = (
                matches[position + 1].start()
                if position + 1 < len(matches)
                else (end_of_context if end_of_context != -1 else len(prompt))
            )
            blocks.append((int(match.group(1)), match.group(2), prompt[start:stop].strip()))
        return blocks

    @staticmethod
    def _parse_question(prompt: str) -> str:
        match = re.search(r"^CÂU HỎI: (.+)$", prompt, re.M)
        return match.group(1).strip() if match else ""

    def _sentences(self, text: str) -> list[str]:
        out = []
        for piece in SENTENCE_SPLIT.split(text):
            cleaned = " ".join(piece.split())
            if len(cleaned) >= self.min_sentence_chars:
                out.append(cleaned)
        return out

    def __call__(self, prompt: str) -> str:
        question = self._parse_question(prompt)
        blocks = self._parse_context(prompt)
        if not question or not blocks:
            return "[trích xuất] Không đọc được ngữ cảnh từ prompt."

        question_vector = self.embedder(question)

        scored: list[tuple[float, int, str, str]] = []
        for number, doc_id, content in blocks:
            for sentence in self._sentences(content):
                score = compute_similarity(question_vector, self.embedder(sentence))
                scored.append((score, number, doc_id, sentence))

        scored.sort(key=lambda item: -item[0])
        picked = [item for item in scored if item[0] >= self.min_score][: self.max_sentences]

        if not picked:
            best = scored[0][0] if scored else 0.0
            return (
                "[trích xuất] Ngữ cảnh truy xuất được không đủ liên quan để trả lời "
                f"(câu sát nhất chỉ đạt {best:.3f} < ngưỡng {self.min_score}). "
                "Cần thu hẹp truy vấn hoặc bổ sung tài liệu."
            )

        lines = [
            f"- {sentence} [{number}]  (nguồn: {doc_id}, độ liên quan {score:.3f})"
            for score, number, doc_id, sentence in picked
        ]

        # Nếu các câu được chọn đến từ nhiều tài liệu khác nhau thì nói thẳng —
        # trong corpus 5 trường, đó thường là dấu hiệu đang trộn quy định của
        # hai trường vào một câu trả lời.
        sources = {doc_id for _, _, doc_id, _ in picked}
        note = ""
        if len(sources) > 1:
            note = (
                f"\n\nLƯU Ý: các ý trên đến từ {len(sources)} tài liệu khác nhau "
                f"({', '.join(sorted(sources))}). Kiểm tra xem chúng có cùng áp dụng "
                "cho trường hợp của bạn không trước khi dùng."
            )

        return "[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]\n" + "\n".join(lines) + note
