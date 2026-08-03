# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:*

**Ví dụ có độ tương tự CAO:**
- Câu A:
- Câu B:
- Tại sao tương đồng:

**Ví dụ có độ tương tự THẤP:**
- Câu A:
- Câu B:
- Tại sao khác:

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

Truy xuất bằng `search_with_filter()` (bao luôn `search()` khi không có bộ lọc), rồi ghép
ngữ cảnh dưới dạng khối đánh số `[1] [2] [3]`, mỗi khối kèm `doc_id` và `score`. Đánh số là
để câu trả lời truy ngược được về đúng chunk nào — không có nó thì không chấm được tiêu chí
*Grounding Quality*. Prompt đặt bốn ràng buộc: chỉ dùng ngữ cảnh, dẫn số nguồn cho từng ý,
nêu rõ khi các nguồn mâu thuẫn, và nói "không đủ thông tin" thay vì suy đoán. Khi truy xuất
trả về rỗng thì `answer()` trả câu "không tìm thấy thông tin liên quan" mà **không gọi
`llm_fn`** — trả lời "không biết" đúng lúc là hành vi đúng của RAG, không phải thất bại.

#### Phần mở rộng tự thêm — `scripts/extractive_llm.py`

> **KHÔNG PHẢI YÊU CẦU CỦA ĐỀ.** `exercises.md` chỉ yêu cầu `answer()` truy xuất → tạo
> prompt → gọi `llm_fn`, và `main.py` cung cấp sẵn `demo_llm` (in lại prompt). Toàn bộ
> phần dưới đây là do tôi tự thêm, nằm ngoài `src/`, và có thể bỏ đi mà không ảnh hưởng
> tới 42/42 test.

Lý do thêm: `docs/SCORING.md` chấm 2 điểm cho *"câu trả lời của tác tử chính xác"* và
`docs/EVALUATION.md` bắt xác minh câu trả lời với gold answer — nhưng repo không cấp LLM
thật, cũng không nói lấy API key ở đâu. Với `demo_llm` in lại prompt thì **không xác minh
được gì**. Đây là khoảng trống trong bộ tài liệu của đề, và tôi lấp bằng một tầng trả lời
chạy offline.

`ExtractiveLLM` **không sinh ra chữ mới**: nó tách các câu có sẵn trong chunk đã truy xuất,
chấm từng câu bằng chính `compute_similarity()`, lấy tối đa 3 câu vượt ngưỡng 0.35, rồi ghép
kèm `[n]`. Dưới ngưỡng thì trả về "ngữ cảnh không đủ liên quan" kèm điểm cao nhất đo được.
Ngưỡng 0.35 lấy từ số đo ở Phần 4: cặp câu hoàn toàn không liên quan cho ~0.07, cặp cùng
miền cho ~0.52.

Gọi đây là "câu trả lời do mô hình sinh ra" là mô tả sai sản phẩm. Nó không diễn giải, không
tổng hợp hai nguồn thành một câu, không trả lời được câu hỏi cần suy luận.

**Kết quả chạy trên 5 câu hỏi** ([`report/benchmark/ANSWERS.md`](benchmark/ANSWERS.md)): câu
trả lời **sai ở hầu hết các câu** — nhưng sai vì tầng truy xuất đã hỏng (0/10), không phải
vì tầng trả lời. Đây chính là điều đáng nói: chất lượng câu trả lời là **hệ quả** của chất
lượng truy xuất, không cứu được bằng prompt.

Ca đáng chú ý nhất là Q5. Tác tử trả lời bằng câu *"must submit applications no later than
one month after a student's return to study at VinUniversity"* — nghe khớp hoàn hảo với câu
hỏi "nộp đơn quay lại trước bao lâu", có cả "one month" lẫn "return to study". Nhưng câu đó
nói về **hạn nộp hồ sơ chuyển đổi tín chỉ**, không phải quy trình quay lại sau bảo lưu. Một
câu trả lời trông đúng, dẫn nguồn đầy đủ, truy ngược được về chunk thật — mà vẫn sai. Đó là
kiểu lỗi nguy hiểm nhất của RAG, và là lý do tiêu chí *Factual Accuracy* tồn tại tách khỏi
*Retrieval Precision*.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
