# CONTRACTS — Định dạng đầu ra bắt buộc giữa các role

> Chủ sở hữu: **R4 (Integrator)**. Ba role còn lại **đọc và tuân theo**, không sửa file này.
> Muốn đổi một contract: nhắn R4, R4 sửa và thông báo lại cả nhóm. Lý do ở mục 0.

## 0. Vì sao có file này

Bốn người làm bốn việc khác nhau nhưng phải ra **một** báo cáo nhóm có bảng so sánh cộng
lại được. Cách hỏng phổ biến nhất không phải là ai đó làm sai, mà là bốn người cùng làm
đúng theo bốn định dạng khác nhau — rồi Giờ 4 ngồi gõ tay số của nhau vào một bảng, sai số,
và không ai kiểm tra lại được.

Bốn contract dưới đây chốt **trước** khi ai sản xuất dữ liệu. Ba cái đầu là đầu vào chung,
cái thứ tư (bảng kết quả) là thứ trực tiếp trở thành bảng trong `REPORT_NHOM.md`.

---

## 1. Contract A — Front matter tài liệu

**Ai sinh ra:** R1 · **Ai dùng:** cả bốn người (qua `build_knowledge_base()` trong `ingest.py`)
· **Nơi lưu:** `data/k3_university/<doc_id>.md`

Giữ **đúng schema của hai file mồi** đã có sẵn trong `data/k3_university/` — đủ **8 khóa**,
không thiếu khóa nào, không tự thêm khóa mới cho riêng một file:

```yaml
---
doc_id: k3-library-renewal
title: Quy định gia hạn mượn sách thư viện
audience: student
department: library
language: vi
source_url: https://example.edu/thu-vien/gia-han
retrieved_at: 2026-08-03
document_version: "2026.1"
---

## 1. Phạm vi áp dụng

Nội dung đã làm sạch...
```

| Khóa | Bắt buộc | Quy ước giá trị |
| :-- | :-: | :-- |
| `doc_id` | ✅ | kebab-case, không dấu, tiền tố `k3-`. Đây là khóa `delete_document()` và mọi bảng đối chiếu dùng |
| `title` | ✅ | tiếng Việt có dấu, dùng để in trong báo cáo |
| `audience` | ✅ | đúng một trong `student` \| `faculty` \| `staff` \| `all`. **K3 bắt buộc** |
| `institution` | ✅ | mã trường viết thường, không dấu (`vinuni`, `ueh`, `iuh`, `vnuf`, `ou`). Thêm ở vòng 2 — xem [FAILURE_ANALYSIS](../report/benchmark/FAILURE_ANALYSIS.md): thiếu trường này thì câu hỏi về trường A bị chunk của trường B chiếm top-1, kéo điểm truy xuất về 0 |
| `department` | ✅ | đúng một trong `registration` \| `tuition` \| `scholarship` \| `library` \| `dormitory` |
| `language` | ✅ | `vi` \| `en` |
| `source_url` | ✅ | URL công khai đầy đủ. Bắt buộc theo `docs/DATA_COLLECTION.md` |
| `retrieved_at` | ✅ | `YYYY-MM-DD`, ngày thực sự lấy về |
| `document_version` | ✅ | bọc nháy kép (`"2026.1"`), hoặc ngày hiệu lực `"2025-09-01"`, hoặc số hiệu văn bản. Không biết thì ghi `"unknown"` chứ **không bỏ khóa** |

> Hai file mồi hiện tại dùng `source_url: https://example.edu/...` và
> `license_or_permission: example-template-replace-me` — **đó là template, không phải nguồn
> thật**. Dùng nguyên trạng làm benchmark là vi phạm yêu cầu "nguồn minh bạch" (10 điểm mục 1).
> R1 phải thay bằng nguồn công khai thật hoặc xóa hai file này khỏi corpus.

Ba quy tắc dễ vi phạm:

1. **Không có dòng `---` mở đầu thì `parse_front_matter()` trả về `{}`** và toàn bộ metadata
   biến mất — không báo lỗi, chỉ là mọi câu hỏi cần lọc đều trượt. Kiểm bằng `python ingest.py`.
2. `audience` và `category` là **enum đóng**. Một file ghi `sinh viên` thay vì `student` sẽ
   không bao giờ khớp `metadata_filter={"audience": "student"}` của R3.
3. Giá trị có dấu `:` phải bọc nháy kép, ví dụ `title: "Học phí: mức thu 2025"`.

Kèm theo: `data/k3_university/sources.csv`, giữ nguyên 7 cột đã có sẵn và **thêm một cột
`char_count`** ở cuối:

```csv
doc_id,file_path,title,source_url,retrieved_at,document_version,license_or_permission,char_count
```

`char_count` là số ký tự phần thân (không tính front matter) — R2 cần nó để giải thích vì
sao số chunk khác nhau giữa các tài liệu. Lấy bằng:

```bash
python -c "from ingest import load_documents; [print(d.id, len(d.content)) for d in load_documents('data/k3_university')]"
```

File phải lưu **UTF-8**. Bản mồi hiện tại đang hỏng mã tiếng Việt (`ÄÄƒng kÃ½`) — R1 ghi
đè lại bằng UTF-8, đừng sửa từng ký tự.

---

## 2. Contract B — Bộ câu hỏi đánh giá

**Ai sinh ra:** R3 · **Ai dùng:** cả bốn người · **Nơi lưu:** `data/benchmark_queries.yaml`

**Đúng 5 câu**, không hơn không kém (đề chốt con số này). **Ít nhất 1 câu** có
`metadata_filter` — yêu cầu riêng của K3.

```yaml
queries:
  - id: Q1
    question: "Sinh viên được gia hạn sách tối đa mấy lần?"
    gold_answer: "Tối đa 2 lần, mỗi lần 7 ngày, nếu sách không có người đặt trước."
    gold_doc_id: library-renewal-policy
    metadata_filter: null
    kind: fact

  - id: Q2
    question: "Hạn nộp học phí học kỳ 1 là khi nào?"
    gold_answer: "..."
    gold_doc_id: tuition-payment-deadline
    metadata_filter:
      audience: student
    kind: filtered
```

| Trường | Bắt buộc | Ghi chú |
| :-- | :-: | :-- |
| `id` | ✅ | `Q1`–`Q5`. Mọi bảng kết quả tham chiếu bằng id này |
| `question` | ✅ | tiếng Việt, như cách sinh viên thật sẽ hỏi |
| `gold_answer` | ✅ | **trích được từ tài liệu**, cụ thể và kiểm chứng được. Không suy đoán quy định |
| `gold_doc_id` | ✅ | trùng `doc_id` ở Contract A. Đây là cách máy chấm `rank_of_gold` |
| `metadata_filter` | ✅ | `null` hoặc dict. Ít nhất một câu phải khác `null` |
| `kind` | ✅ | `fact` \| `filtered` \| `multi_doc` \| `paraphrase` \| `edge`. Năm câu **không được trùng kind hết** — đề yêu cầu câu hỏi đa dạng |

Sau khi R3 tuyên bố **QUERY FREEZE**, file này không đổi nữa. Sửa một câu hỏi sau khi có
người đã chạy đồng nghĩa với việc bảng so sánh không còn cộng lại được.

---

## 3. Contract C — Bảng kết quả benchmark (quan trọng nhất)

**Ai sinh ra:** cả bốn người, mỗi người một file · **Ai dùng:** R2 (bảng so sánh), R3 (chấm điểm), R4 (báo cáo)
· **Nơi lưu:** `report/benchmark/<branch>_<chunker>.csv`

Ví dụ: `report/benchmark/role2-strategy-lead_heading.csv`

**Đúng 11 cột, đúng thứ tự này, một dòng cho mỗi câu hỏi (5 dòng/người):**

```csv
query_id,member_branch,strategy,params,n_chunks_total,rank_of_gold,hit_top3,top1_score,top1_doc_id,top3_doc_ids,rubric_score
Q1,role2-strategy-lead,heading,"level=2",143,1,true,0.8123,library-renewal-policy,"library-renewal-policy|library-renewal-policy|dorm-rules",2
Q2,role2-strategy-lead,heading,"level=2",143,4,false,0.6011,dorm-rules,"dorm-rules|tuition-late-fee|library-renewal-policy",0
```

| Cột | Kiểu | Định nghĩa |
| :-- | :-- | :-- |
| `query_id` | `Q1`–`Q5` | theo Contract B |
| `member_branch` | text | tên branch, dùng thay cho tên người |
| `strategy` | enum | `fixed` \| `sentence` \| `recursive` \| `heading` |
| `params` | text | tham số thật đã dùng, ví dụ `chunk_size=400,overlap=80` |
| `n_chunks_total` | int | `store.get_collection_size()` sau khi nạp **toàn bộ** corpus |
| `rank_of_gold` | int | vị trí (1-based) của chunk đầu tiên có `metadata.doc_id == gold_doc_id`. **Không tìm thấy trong top-10 thì ghi `99`** |
| `hit_top3` | bool | `true` nếu `rank_of_gold <= 3` |
| `top1_score` | float 4 chữ số | điểm của kết quả hạng 1 |
| `top1_doc_id` | text | `doc_id` của kết quả hạng 1 |
| `top3_doc_ids` | text | ba `doc_id` nối bằng dấu `\|` (giữ nguyên thứ tự) |
| `rubric_score` | 0/1/2 | chấm theo `docs/SCORING.md`: **2** = gold ở top-1 và agent trả lời đúng · **1** = gold trong top-3 nhưng không phải top-1, hoặc câu trả lời thiếu chi tiết · **0** = gold không có trong top-3 |

Ba điều kiện để một file CSV được tính là bằng chứng hợp lệ:

- Chạy **sau** corpus freeze và query freeze, trên `main` đã pull mới nhất.
- `EMBEDDING_PROVIDER=local` và đã xác nhận `_backend_name` **không** phải mock.
- 42/42 test pass trên `src/` của người chạy.

Ghi ngay ba điều kiện này thành 3 dòng comment `#` ở đầu file CSV, kèm ngày chạy.

Vì sao đúng bộ cột này: `n_chunks_total` giải thích **quy mô**, `rank_of_gold` đo **chất
lượng thật** (khác hẳn `hit_top3` — top-1 và top-3 là hai chất lượng khác nhau, rubric chấm
2đ so với 1đ), `top1_doc_id` chỉ ra **nhầm sang tài liệu nào** khi trượt, và đó thường là
toàn bộ nội dung phần phân tích lỗi.

---

## 4. Contract D — Kết quả baseline comparator

**Ai sinh ra:** R2 · **Nơi lưu:** `report/strategy/baseline_<doc_id>.json`

Ghi nguyên văn dict trả về từ `ChunkingStrategyComparator().compare(text, chunk_size=...)`,
bọc thêm ba khóa ngữ cảnh:

```json
{
  "doc_id": "library-renewal-policy",
  "chunk_size": 200,
  "embedding_backend": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
  "comparison": { "...": "nguyên văn output của compare()" }
}
```

Chạy trên **2–3 tài liệu** theo yêu cầu Bài tập 3.1 Bước 1 — nên chọn tài liệu có cấu trúc
khác nhau rõ rệt (một cái nhiều heading, một cái văn xuôi liền mạch), vì đó là điều kiện để
phần so sánh nói được cái gì.

---

## 5. Bảng ghép cuối cùng

R4 gom bằng lệnh này, không gõ tay:

```bash
python scripts\merge_benchmark.py report\benchmark\ --output report\benchmark\ALL.csv
```

`ALL.csv` (20 dòng = 4 người × 5 câu) là nguồn duy nhất cho:

| Đích đến | Cách dùng |
| :-- | :-- |
| `REPORT_NHOM.md` §3 — Tổng hợp chất lượng truy xuất | pivot `rubric_score` theo `query_id` × `member_branch` |
| `REPORT_NHOM.md` §2 — So sánh giữa các thành viên | pivot `rank_of_gold`, kèm `n_chunks_total` |
| `REPORT_NHOM.md` §4 — Phân tích lỗi | lọc `rubric_score == 0`, đọc `top1_doc_id` để biết nhầm sang đâu |
| `REPORT_CANHAN.md` §5 — Kết quả của tôi | lọc `member_branch` của mình |

Một dòng trong `ALL.csv` sai định dạng sẽ hỏng cả bốn bảng cùng lúc. Vì vậy
`merge_benchmark.py` kiểm tra header, enum và kiểu dữ liệu trước khi ghép, và **báo lỗi
thay vì bỏ qua dòng hỏng**.
