# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> *1 câu — ví dụ: thư viện + đăng ký môn học.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `ou-quy-che-hoc-vu-tin-chi` | `fixed_size` | 255 | 199.81 | Không ổn định: có ranh giới cắt giữa từ/câu |
|  | `by_sentences` | 79 | 479.52 | Giữ câu nhưng có chunk dài tới 1,535 ký tự |
|  | `recursive` | 228 | 164.88 | Khống chế kích thước, có thể mất tên điều |
|  | `heading` | 47 | 817.53 | Giữ tiêu đề/điều khoản; section dài được chia tiếp |
| `vinuni-academic-regulations-undergrad` | `fixed_size` | 459 | 199.72 | Có thể cắt ngang bảng hoặc điều khoản |
|  | `by_sentences` | 152 | 449.85 | Giữ câu, độ dài dao động lớn |
|  | `recursive` | 537 | 126.46 | Có nhiều mẩu rất ngắn, min 2 ký tự |
|  | `heading` | 79 | 892.86 | Giữ heading nhưng một số section cùng chủ đề cạnh tranh nhau |
| `vinuni-credit-transfer` | `fixed_size` | 34 | 199.79 | Độ dài đều nhưng không theo ranh giới mục |
|  | `by_sentences` | 9 | 568.22 | Giữ câu, độ lệch 314.87 ký tự |
|  | `recursive` | 39 | 130.10 | Có mẩu ngắn 22 ký tự |
|  | `heading` | 5 | 1070.20 | Mỗi mục gần một đơn vị ngữ nghĩa hoàn chỉnh |

Số liệu lấy từ `report/strategy/heading_comparison.json`, chạy sau khi bỏ YAML front matter,
với baseline `chunk_size=200` và local multilingual embedder. Ví dụ đọc được về fixed-size
cắt hỏng và heading giữ nguyên nằm trong `report/strategy/HEADING_COMPARISON.md`.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Role 2 — Nguyễn Chí Hướng (`01203_NguyenChiHuong`)**
- **Loại chiến lược:** custom `HeadingChunker(max_level=2, max_chars=1200)`.
- **Mô tả & lý do chọn:** Quy định học vụ được tổ chức theo Chương/Điều/Article nên heading
  là ranh giới ngữ nghĩa tự nhiên. Mục dài được chia tiếp bằng `RecursiveChunker`, mục ngắn
  được gộp với mục tiếp theo, phần trước heading không bị bỏ, và heading được đính lại vào
  mọi mảnh con để giữ provenance/ngữ cảnh.
- **Kết quả benchmark cá nhân:** 218 chunks; gold `doc_id` trong top-3 ở 5/5 nhưng chỉ 2/5
  query có chunk chứa bằng chứng, tổng rubric nghiêm ngặt 2/10. Điều này cho thấy đúng document
  không đồng nghĩa đúng section.
- **Đối chứng Recursive:** `chunk_size=400`, 598 chunks, gold `doc_id` top-3 ở 3/5, chỉ 1/5
  query có đủ bằng chứng và rubric 1/10. Heading tốt hơn về coverage dù collection nhỏ hơn.

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | VinUni: tối đa bao nhiêu tín chỉ trong kỳ chính mà không cần Dean duyệt? | 22 tín chỉ; 18–22 là automatic overload, trên 22 cần Dean duyệt | `vinuni-academic-regulations-undergrad` — bảng Study load variation |
| 2 | Withdraw muộn nhất khi nào và cả khóa tối đa bao nhiêu tín chỉ? | Trước khi hoàn thành quá 30% thời lượng; tối đa 18 tín chỉ | `vinuni-academic-regulations-undergrad` — Article 12 |
| 3 | Chuyển tín chỉ tối đa bao nhiêu và nộp lúc nào? | Không quá 50%; nộp tuần đầu học kỳ | `vinuni-credit-transfer` — mục 3.1 và 3.2 |
| 4 | Chưa đóng học phí có bị mất môn không? | Có; UEH hủy học phần chưa đóng học phí sau hạn | `ueh-dang-ky-huy-hoc-phan` — Điều 4/Điều 6 |
| 5 | Xin quay lại sau bảo lưu trước bao lâu? | Quy trình ghi 1 tháng, Academic Regulations ghi 1 tuần; phải nêu mâu thuẫn | `vinuni-leave-of-absence` và `vinuni-academic-regulations-undergrad` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, rõ nhất ở Q2. Với `audience=student, institution=vinuni`, chunk Article 12 chứa đáp án
> lên hạng 2. Khi bỏ filter, top-3 trở thành hai chunk VNUF và một chunk UEH, không còn quy
> định VinUni. Filter giảm nhiễu giữa các trường nhưng không giải quyết được lỗi đúng tài
> liệu/sai section, nên vẫn phải chấm bằng nội dung chunk thay vì chỉ `doc_id`.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
