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

**Phạm vi cụ thể nhóm tập trung:** Học vụ và đăng ký học phần — điều kiện đăng ký, giới hạn
tín chỉ, rút/hủy học phần, bảo lưu, chuyển đổi tín chỉ.

Chọn lát cắt hẹp này vì văn bản nguồn được viết theo **điều/khoản có tiêu đề rõ ràng**, tức
ranh giới mục mang ngữ nghĩa thật — điều kiện để so sánh chunking theo heading với chunking
theo kích thước cố định nói lên được điều gì đó. Corpus rải đều năm lĩnh vực thì câu hỏi nào
cũng dễ, retrieval trông giỏi hơn thực tế và không có gì để phân tích.

### Danh sách tài liệu (Data Inventory)

10 tài liệu, 5 trường, 2 ngôn ngữ. Kiểm kê máy đọc được:
[`data/k3_university/sources.csv`](../data/k3_university/sources.csv) · quyết định thu thập:
[`data/PROVENANCE-k3-university.md`](../data/PROVENANCE-k3-university.md).

| # | doc_id | Nguồn | Lấy / Phiên bản | Ký tự | Metadata |
|:-:|---|---|---|--:|---|
| 1 | `vinuni-academic-regulations-undergrad` | policy.vinuni.edu.vn | 2026-08-03 / not-stated | 68.770 | student, vinuni, en |
| 2 | `ou-quy-che-hoc-vu-tin-chi` | v1.ou.edu.vn | 2026-08-03 / not-stated | 38.251 | student, ou, vi |
| 3 | `vnuf-huong-dan-quy-che-tin-chi` | vnuf.edu.vn | 2026-08-03 / not-stated | 37.187 | **faculty**, vnuf, vi |
| 4 | `ueh-dang-ky-huy-hoc-phan` | daotao.ueh.edu.vn | 2026-08-03 / not-stated | 9.433 | student, ueh, vi |
| 5 | `vinuni-leave-of-absence` | policy.vinuni.edu.vn | 2026-08-03 / not-stated | 7.398 | student, vinuni, en |
| 6 | `vinuni-registrar-policy-index` | registrar.vinuni.edu.vn | 2026-08-03 / not-stated | 5.476 | **staff**, vinuni, en |
| 7 | `vinuni-credit-transfer` | policy.vinuni.edu.vn | 2026-08-03 / not-stated | 5.143 | student, vinuni, en |
| 8 | `vinuni-registrar-faqs` | registrar.vinuni.edu.vn | 2026-08-03 / not-stated | 4.776 | student, vinuni, en |
| 9 | `vinuni-class-schedule-registration` | registrar.vinuni.edu.vn | 2026-08-03 / not-stated | 3.973 | student, vinuni, en |
| 10 | `iuh-huong-dan-dang-ky-hoc-phan` | camnang.iuh.edu.vn | 2026-08-03 / not-stated | 2.747 | student, iuh, vi |

**Ba lựa chọn có chủ đích:**

- **Giữ 2 tài liệu `audience` khác `student`** (#3, #6). Không có chúng thì
  `metadata_filter={"audience": "student"}` không lọc đi thứ gì, và câu hỏi bắt buộc của K3
  không chứng minh được điều gì.
- **Trộn `vi` + `en`.** `language` thành trục lọc thật, đồng thời kiểm luôn khả năng đa ngữ
  của embedder. Quyết định này về sau hoá ra là **nguyên nhân lỗi lớn nhất** — xem Phần 4.
- **Nhiều trường khác nhau.** Ban đầu là tình cờ (VinUni không đủ tài liệu công khai), sau
  thành phép thử tốt nhất cho giá trị của metadata filtering.

**Danh sách kiểm tra quản trị dữ liệu:**
- [x] Corpus chỉ chứa nguồn công khai; không có dữ liệu cá nhân, thông tin đăng nhập, tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata.
- [x] Hai file mồi của lớp (`course-registration.md`, `library-services.md`) đã **gỡ bỏ** —
      `source_url` của chúng là `https://example.edu/...`, dùng làm benchmark là gian lận nguồn.
- [x] Một nguồn (`ctsv.ued.udn.vn`) bị **loại** vì trả về trang "Browser Verification" của
      WAF. Không vượt qua bằng cách giả lập trình duyệt — `DATA_COLLECTION.md` mục 2.3 cấm.

> **Điểm yếu trung thực:** cả 10 tài liệu đều `document_version: not-stated`. Trang policy
> của VinUni nạp ngày hiệu lực bằng JavaScript nên không crawl được; các trang tiếng Việt
> không nêu số hiệu trong phần thân. `DATA_COLLECTION.md` mục 4 cho phép giá trị này, nhưng
> nó có nghĩa là corpus **không kiểm được độ mới của quy định**.

### Cấu trúc Metadata (Metadata Schema)

9 khoá bắt buộc cho mọi tài liệu. Đặc tả: [`docs/CONTRACTS.md`](../docs/CONTRACTS.md) §1.

| Trường | Kiểu | Ví dụ | Tại sao hữu ích cho truy xuất |
|---|---|---|---|
| `doc_id` | chuỗi | `vinuni-credit-transfer` | Khoá để `delete_document()` và để chấm `rank_of_gold` |
| `title` | chuỗi | "Quy định đăng ký và hủy học phần (UEH)" | Hiển thị nguồn trong câu trả lời của agent |
| `audience` | enum | `student` \| `faculty` \| `staff` \| `all` | **K3 bắt buộc.** Chặn tài liệu hướng dẫn giảng viên chiếm top-1 khi sinh viên hỏi |
| `institution` | enum | `vinuni`, `ueh`, `ou` | **Thêm ở vòng 2.** Thiếu nó thì hỏi về trường A nhận về quy định trường B — nguyên nhân của 0/10 vòng đầu |
| `department` | enum | `dao-tao`, `registrar` | Thu hẹp khi hai lĩnh vực dùng chung từ vựng ("gia hạn" có ở cả thư viện lẫn học phí) |
| `language` | enum | `vi` \| `en` | Cho phép ép truy vấn về đúng ngôn ngữ tài liệu — cần thiết vì khoảng cách xuyên ngữ ở cấp chunk rất lớn |
| `source_url` | URL | `https://policy.vinuni.edu.vn/...` | Truy vết câu trả lời về văn bản gốc |
| `retrieved_at` | ngày | `2026-08-03` | Biết dữ liệu cũ bao lâu |
| `document_version` | chuỗi | `not-stated` | Kiểm tra quy định còn hiệu lực không |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

`chunk_size=500`, số liệu thô: [`report/strategy/`](strategy/).

| Tài liệu | Chiến lược | Chunk | Dài TB | **Độ lệch** | Dài nhất | Giữ ngữ cảnh? |
|---|---|--:|--:|--:|--:|---|
| `vinuni-academic-regulations` | `fixed_size` | 153 | 499.2 | 10.5 | 500 | Không — cắt ngang câu |
| | `by_sentences` | 154 | 444.0 | **205.6** | **1868** | Trọn câu, nhưng dài ngắn thất thường |
| | `recursive` | 183 | 373.8 | 101.0 | 500 | Có — cắt ở ranh giới đoạn |
| `vinuni-credit-transfer` | `fixed_size` | 12 | 474.4 | 84.9 | 500 | Không |
| | `by_sentences` | 9 | 568.2 | **314.9** | 1162 | Thất thường |
| | `recursive` | 15 | 341.0 | 134.5 | 497 | Có |
| `ou-quy-che-hoc-vu` | `fixed_size` | 85 | 499.3 | 6.6 | 500 | Không |
| | `by_sentences` | 114 | 327.8 | 175.7 | 1054 | Thất thường |
| | `recursive` | 81 | 470.1 | **24.8** | 500 | Có — bám được Chương/Điều |

**Cột độ lệch chuẩn là cột nói nhiều nhất, và nó không có trong mẫu báo cáo.** Trung bình che
mất một điều quan trọng: `by_sentences` gom đúng 3 câu bất kể dài ngắn nên **không hề tôn
trọng `chunk_size`** — nó đẻ ra chunk 1868 ký tự nằm cạnh chunk 156 ký tự. Với văn bản quy
định, một "câu" có thể là cả một khoản liệt kê dài. Chunk quá dài pha loãng embedding, chunk
quá ngắn thiếu ngữ cảnh; cả hai đầu đều kéo thứ hạng xuống.

`ou-quy-che-hoc-vu` là ca ngược lại đáng chú ý: `recursive` cho **ít chunk hơn** `fixed_size`
(81 so với 85) mà độ lệch chỉ 24.8 — tài liệu tiếng Việt này có nhiều `\n\n` ở ranh giới
Điều/Khoản nên đệ quy bám được cấu trúc thật thay vì cắt bừa.

### Chiến lược của từng thành viên

**Lê Quang Huy (2A202601821)** — `RecursiveChunker`, `chunk_size=500`

Cắt theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]` — cắt ở chỗ ít gây tổn hại nhất.
Chọn 500 sau khi quét 300/500/800 ([`CHUNK_SIZE_SWEEP.md`](strategy/CHUNK_SIZE_SWEEP.md)):
đó là ngưỡng lớn nhất còn nằm dưới giới hạn **128 token** của
`paraphrase-multilingual-MiniLM-L12-v2` (500 ký tự ≈ 112 token tiếng Việt). Vượt ngưỡng thì
mô hình cắt cụt phần đuôi **mà không báo gì**.

**Nguyễn Chí Hướng (2A202601203)** — `HeadingChunker` (custom) — *đáp ứng yêu cầu K3*

Cắt theo tiêu đề mục thay vì theo hình thức trình bày. Nhận diện cả heading Markdown lẫn
dòng pháp quy tiếng Việt, và **đính lại tiêu đề vào từng mảnh con** khi mục dài quá hạn:

```python
_LEGAL_HEADING_RE = re.compile(
    r"^(?:chương|điều|phần|mục|chapter|article|part|section)\s+"
    r"(?:[ivxlcdm]+|\d+(?:\.\d+)*[a-z]?)(?:\s*[.):\-–—]|\s+|$).*",
    re.IGNORECASE)

def _split_long_section(self, section):
    ...
    return [f"{heading}\n\n{piece}".strip() for piece in body_chunks]
```

Nguồn: nhánh `2A202601203-NguyenChiHuong`, `scripts/custom_chunkers.py`.

**Phạm Thị Liên (2A202601795)** — `RecursiveChunker` / `SentenceChunker`, có `bench.py` riêng.
**Nguyễn Tiến Đạt (2A202601387)** — vai Benchmark & Evaluation Designer, có `bench.py`, `check.py`.

### Chạy chéo: cùng chiến lược, khác `src/`

Để tách biến "chiến lược" khỏi biến "cách lập trình", nhóm chạy **cùng một** `HeadingChunker`
(`max_chars=800`), **cùng** corpus, **cùng** 5 câu hỏi — chỉ đổi `src/` của từng người. Bốn
file CSV gộp bằng [`scripts/merge_benchmark.py`](../scripts/merge_benchmark.py) thành
[`ALL.csv`](benchmark/ALL.csv) (25 dòng, 5 lần chạy).

| Thành viên | Chiến lược | Chunk | **Điểm** |
|---|---|--:|:-:|
| Phạm Thị Liên | `heading` 800 | **321** | 8/10 |
| Lê Quang Huy | `heading` 800 | 318 | 8/10 |
| Nguyễn Chí Hướng | `heading` 800 | 318 | 8/10 |
| Lê Quang Huy | `recursive` 500 | 456 | 6/10 |
| **Nguyễn Tiến Đạt** | `heading` 800 | 318 | **0/10** |

Hai kết quả bất thường, cả hai đều là **lỗi `src/` mà 42/42 test không bắt được**:

**1. Đạt: 0/10 dù pass toàn bộ test.** Nguyên nhân nằm ở đúng một dòng trong `_make_record`:

```python
meta["doc_id"] = doc.id        # Đạt  — ghi đè
metadata.setdefault("doc_id", doc.id)   # Hướng — giữ nguyên nếu đã có
```

`ingest.chunk_document()` đã đặt `metadata["doc_id"]` là id của **tài liệu cha**, còn `doc.id`
lúc này là id của **chunk** (`vinuni-academic-regulations-undergrad::chunk_43`). Gán đè biến
mọi `doc_id` thành id chunk, nên store báo *"318 chunk từ **318 tài liệu**"* và mọi phép đối
chiếu `gold_doc_id` đều trượt. `delete_document()` cũng hỏng theo.

Test không bắt được vì test tạo `Document` có `id` trùng luôn `doc_id` và `metadata` rỗng —
trong ca đó gán đè cho kết quả y hệt `setdefault`.

**2. Liên: 321 chunk thay vì 318** dù chạy cùng `HeadingChunker`. Vì
`HeadingChunker._split_long_section()` gọi lại `RecursiveChunker` trong `src/chunking.py` của
mỗi người, mà cách gộp mảnh của bạn ấy khác một chút (thêm dấu phân cách vào **đầu** mảnh,
nhóm dùng cách nối bằng separator). Chênh 3 chunk, **không đổi điểm** — nhưng cho thấy
"cùng chiến lược" vẫn không có nghĩa là "cùng kết quả" khi phần dùng chung nằm trong `src/`.

> Ba bạn chưa tự chạy; các số trên do nhóm trưởng chạy hộ bằng `git worktree` với `src/` của
> từng người trên cùng cây `main`. Bài tập 3.4 muốn **mỗi người tự chạy trên máy mình** —
> đây là điểm nhóm chưa làm đúng quy trình, dù số liệu là thật.

### So Sánh Giữa Các Thành Viên

| Chiến lược | Chunk | Dài TB | top-3 | **Điểm** | rank Q1→Q5 |
|---|--:|--:|:-:|:-:|---|
| `recursive` 300 | 836 | 217 | 3/5 | 6/10 | 1, 1, 9, 1, 99 |
| `recursive` **500** (Huy) | 456 | 400 | 3/5 | 6/10 | 1, 1, 6, 1, 5 |
| `recursive` 800 | 267 | 684 | 3/5 | 6/10 | 2, 1, 2, 1, 9 |
| `heading` 550 | 462 | 424 | 5/5 | 7/10 | 2, 1, 3, 1, 3 |
| **`heading` 800** (Hướng) | **318** | **599** | **5/5** | **8/10** | **1, 1, 2, 1, 2** |
| `heading` 1200 | 217 | 860 | 5/5 | 7/10 | 2, 1, 3, 1, 2 |

| Thành viên | Chiến lược | Điểm | Điểm mạnh | Điểm yếu |
|---|---|:-:|---|---|
| Nguyễn Chí Hướng | `heading` 800 | **8/10** | 5/5 lọt top-3; bám ranh giới điều khoản; giữ tiêu đề trong mọi chunk | 66% chunk vượt trần token; phụ thuộc tài liệu có heading rõ |
| Lê Quang Huy | `recursive` 500 | 6/10 | Không chunk nào vượt trần token; ổn định trên mọi loại văn bản | Cắt theo hình thức trình bày, mất ranh giới ngữ nghĩa; trượt Q3 và Q5 ở mọi tham số |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

`HeadingChunker` — **5/5 lọt top-3 so với 3/5**, và hai câu `recursive` luôn trượt (Q3, Q5)
đều được nó kéo lên hạng 2.

Khác biệt **không** đến từ kích thước chunk. `recursive` 800 và `heading` 800 gần bằng nhau
(684 vs 599 ký tự) nhưng chênh 2 điểm và chênh 2 câu top-3. Nó đến từ **chỗ đặt nhát cắt**:
`recursive` cắt theo `\n\n`/`\n`/`. ` tức theo *hình thức trình bày*, còn `heading` cắt theo
`Điều`/`Chương`/`Article` — ranh giới do **người soạn văn bản** đặt ra. Với quy định học vụ,
mỗi điều là một đơn vị trả lời trọn vẹn, nên ranh giới đó chính là thứ ta muốn.

Chi tiết quyết định nhất là `_split_long_section` đính lại tiêu đề vào từng mảnh con. Chunk
lúc được truy xuất thì đứng một mình, không còn ngữ cảnh xung quanh; tiêu đề là mẩu ngữ cảnh
rẻ nhất có thể đính vào.

**Một kết quả bác bỏ kết luận của chính nhóm.** Nhóm từng đo được mô hình chỉ nhận 128 token
và kết luận nên giữ chunk dưới ~550 ký tự để không bị cắt cụt. Nhưng cấu hình **tốt nhất** lại
là cấu hình có **66% số chunk vượt trần** (210/318):

| `heading` max_chars | Chunk bị cắt cụt | Điểm |
|--:|---|:-:|
| 550 | 67/462 (14%) | 7/10 |
| **800** | **210/318 (66%)** | **8/10** |
| 1200 | 174/217 (80%) | 7/10 |

Lời giải: cắt cụt cắt phần **đuôi**, mà `HeadingChunker` đặt tiêu đề ở **đầu** — nên thông
tin định danh quan trọng nhất luôn sống sót. Vượt trần token không nguy hiểm bằng việc **để
phần quan trọng nằm ở đuôi**. Kết luận cũ đúng với `RecursiveChunker`, không áp dụng được cho
chunker biết đặt tiêu đề lên trước.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

Nguồn máy đọc được: [`data/benchmark_queries.yaml`](../data/benchmark_queries.yaml) ·
diễn giải: [`report/benchmark/QUERIES.md`](benchmark/QUERIES.md).

| # | Câu hỏi | Câu trả lời chuẩn (rút gọn) | Chunk nào chứa thông tin |
|:-:|---|---|---|
| Q1 `fact` | Ở VinUni, tối đa bao nhiêu tín chỉ/kỳ mà không phải xin phê duyệt? | **22 tín chỉ.** 18–22 là automatic overload (Advisor/Program Director xem xét); trên 22 cần College Dean duyệt | `vinuni-academic-regulations` — bảng *Study load variation* |
| Q2 `filtered` | Rút học phần muộn nhất khi nào, cả khóa tối đa bao nhiêu tín chỉ? | Trước khi hoàn thành quá **30%** thời lượng môn; nhận điểm **W**; toàn khóa tối đa **18 tín chỉ** | `vinuni-academic-regulations` — *Article 12* |
| Q3 `multi_doc` | Chuyển đổi tín chỉ tối đa bao nhiêu, nộp hồ sơ lúc nào? | Không quá **50%** tổng tín chỉ; nộp **tuần đầu học kỳ**, xử lý trong 1 tuần sau add/drop | `vinuni-credit-transfer` §3.1–3.2 **và** `vinuni-academic-regulations` Article 13 |
| Q4 `paraphrase` | Đăng ký môn rồi chưa nộp tiền học thì có mất môn không? | **Có** — quá hạn đóng học phí, Trường hủy học phần trên hệ thống | `ueh-dang-ky-huy-hoc-phan` — *Điều 4* |
| Q5 `edge` | Sau bảo lưu, nộp đơn quay lại trước bao lâu? | **Corpus mâu thuẫn**: Regulations ghi *1 tuần*, Procedure ghi *1 tháng* | `vinuni-academic-regulations` **và** `vinuni-leave-of-absence` |

Năm `kind` khác nhau là có chủ đích — mỗi loại làm hỏng retrieval theo một kiểu riêng. Q2 là
câu bắt buộc của K3 (cần `metadata_filter`); Q1 là câu dễ nhất, dùng làm "cầu chì": Q1 mà
trượt thì lỗi nằm ở hệ thống (store rỗng, embedder là mock) chứ không phải ở chiến lược.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Chiến lược tốt nhất cho câu này | Top-3 có chunk liên quan? | Điểm | Ghi chú |
|:-:|---|:-:|:-:|---|
| Q1 | `heading` 800 (hạng 1) | ✅ cả hai | 2 | `recursive` cũng hạng 1, **nhưng** đoạn chứa "18-22 credits" nằm ở hạng 71 |
| Q2 | Hoà — cả hai hạng 1 | ✅ cả hai | 2 | Câu duy nhất bộ lọc `audience` có việc thật |
| Q3 | `heading` (hạng 2) vs `recursive` (hạng 6) | ⚠️ chỉ `heading` | 1 | Đáp án ở **2 tài liệu**, Contract B chỉ khai được 1 |
| Q4 | Hoà — cả hai hạng 1 | ✅ cả hai | 2 | Phép đo **suy biến**: pool chỉ còn 1 tài liệu sau khi lọc |
| Q5 | `heading` (hạng 2) vs `recursive` (hạng 5) | ⚠️ chỉ `heading` | 1 | Như Q3 — đáp án ở 2 tài liệu |

**Tổng: `heading` 8/10 · `recursive` 6/10.**

Có câu đảo chiều thắng-thua không? **Không có câu nào `recursive` thắng `heading`** — đây là
kết quả sạch, chiến lược heading thắng đều. Nhưng có đảo chiều giữa các **tham số**:
`recursive` 800 đưa Q3 lên hạng 2 (+1đ) trong khi đánh rơi Q1 từ hạng 1 xuống 2 (−1đ), tổng
vẫn 6/10. Ba cấu hình `recursive` đều ra đúng 6/10 bằng ba đường khác nhau — **chỉ số của
rubric quá thô để chọn tham số**.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

Giúp, và đây là phát hiện lớn nhất của nhóm. Vòng chạy đầu **không có** trường `institution`:
**0/10, cả 5 câu đều trượt.** Câu hỏi ghi rõ "VinUni" nhưng embedding không đánh trọng số cho
tên trường — nó chỉ thấy "sinh viên", "tín chỉ", "học kỳ" — nên chunk của ĐH Lâm nghiệp, ĐH
Mở, UEH chiếm hết top-3.

Thêm `institution` vào metadata và vào `metadata_filter`, **không đổi gì khác**:

| # | rank không lọc | rank có lọc |
|:-:|--:|--:|
| Q1 | 7 | **1** |
| Q2 | 5 | **1** |
| Q4 | 8 | **1** |
| Q5 | 99 | 5 |

**0/10 → 6/10.** Ví dụ rõ nhất là Q2: không lọc thì tài liệu hạng 1 là
`vnuf-huong-dan-quy-che-tin-chi` (`audience=faculty`) — Điều 11 của nó dùng đúng cụm "rút bớt
học phần" tiếng Việt và nêu mốc 6–8 tuần. Đọc lên rất thuyết phục, điểm số cao nhất (0.6664),
và **sai**, vì đó là quy định trường khác. Điểm số không cứu được; chỉ metadata mới loại được nó.

Điều này khớp với thí nghiệm ở phần dự đoán độ tương tự: hai câu "rút học phần" và "rút tiền
ATM" đạt 0.60 — cao hơn hai quy định *thật sự cùng miền* (0.52). Ngưỡng lọc theo điểm kiểu
"chỉ nhận score > 0.5" vừa nhận thứ lạc đề vừa suýt loại thứ đúng.

> **Trung thực về con số 6/10:** 2 điểm của Q4 không đáng tin. Lọc `institution=ueh` để lại
> pool 23 chunk từ **một** tài liệu, mà `rank_of_gold` đo ở mức tài liệu — hạng 1 gần như
> được cho không. Điểm thật đáng tin là **Q1 + Q2 = 4/10**, cả hai lọc `vinuni` với pool 250
> chunk / 6 tài liệu.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích hay nhất nhóm sẽ trình bày:**

1. **Metadata cứu được bài, điểm số thì không — 0/10 lên 6/10 chỉ bằng một trường.** Không có
   `institution`, cả 5 câu đều bị chunk của trường khác chiếm top-1 với **điểm cao hơn** tài
   liệu đúng. Thứ embedding không phân biệt được thì metadata phân biệt được.

2. **`rank_doc = 1` không có nghĩa agent đọc được câu trả lời.** Q1 với `recursive` được 2
   điểm rubric, nhưng đoạn chứa "18-22 credits" nằm ở **hạng 71** — tài liệu lên hạng 1 nhờ
   một chunk khác. Rubric chấm ở mức **tài liệu**, agent đọc ở mức **chunk**, và điểm số che
   mất khoảng lệch đó. Đây là lý do nhóm tự thêm chỉ số `rank_needle` bên cạnh `rank_of_gold`.

3. **Một câu trả lời có trích dẫn đầy đủ vẫn có thể sai.** Ở Q5, tác tử trả lời *"must submit
   applications no later than one month after a student's return to study"* — dẫn nguồn được,
   truy ngược về chunk thật được, đọc lên khớp hoàn hảo. Nhưng câu đó nói về **hạn nộp hồ sơ
   chuyển đổi tín chỉ**, không phải quy trình quay lại sau bảo lưu. Dẫn được nguồn ≠ đúng.

4. **Vượt trần token không nguy hiểm bằng để phần quan trọng nằm ở đuôi.** Mô hình chỉ nhận
   128 token, vậy mà cấu hình tốt nhất có 66% chunk vượt trần — vì `HeadingChunker` đặt tiêu
   đề ở đầu, và cắt cụt thì cắt đuôi.

**Bài học rút ra khi so sánh trong nhóm:**

Cùng corpus, cùng câu hỏi, cùng embedder — chỉ đổi chỗ đặt nhát cắt mà chênh 2 điểm và chênh
2 câu lọt top-3. Cắt theo **hình thức trình bày** (`\n\n`, `\n`) thua cắt theo **ranh giới
ngữ nghĩa** (`Điều`, `Chương`, `Article`), vì với văn bản quy định thì mỗi điều là một đơn vị
trả lời trọn vẹn. Kích thước chunk gần như không giải thích được gì: `recursive` 800 và
`heading` 800 chênh nhau 85 ký tự trung bình mà chênh 2 điểm.

Bài học về **phương pháp** cũng đáng kể: nhóm đổi **đúng một biến mỗi vòng**. Nếu vòng 2 sửa
cùng lúc `institution` lẫn nhãn gold thì 0/10 → 8/10 trông rất đẹp mà không giải thích được
phần nào đến từ đâu. Con số nhỏ hơn nhưng nói được nhiều hơn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu?**

1. **Corpus một trường, hoặc gắn `institution` ngay từ đầu.** Trộn 5 trường là nguyên nhân
   trực tiếp của 0/10 vòng đầu. Nó vô tình thành phép thử tốt cho metadata filtering, nhưng
   đó là may chứ không phải thiết kế.

2. **Không trộn hai ngôn ngữ khi câu hỏi chỉ có một.** Đo được: giữ nguyên chunk vàng, chỉ
   đổi ngôn ngữ câu hỏi từ Việt sang Anh, thứ hạng nhảy từ **192/456 lên 19/456**. Nhóm từng
   kết luận "trộn vi/en an toàn" dựa trên phép thử hai câu ngắn dịch sát nghĩa (0.77) — kết
   luận đó **sai**, vì thực tế là so câu hỏi ngắn với khối 500 ký tự lẫn bảng biểu.

3. **`gold_doc_ids` dạng danh sách thay vì một `gold_doc_id`.** Q3 và Q5 có đáp án ở hai tài
   liệu; hệ thống đưa nội dung đúng lên hạng 1–2 mà máy chấm vẫn báo trượt. Đây là lỗi của
   **thước đo**, và nó làm mất 4 điểm không đáng mất.

4. **Chốt `document_version` thật.** Cả 10 tài liệu đều `not-stated`, nghĩa là corpus không
   kiểm được độ mới của quy định — với dữ liệu học vụ thì đó là thiếu sót đáng kể.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá | Căn cứ |
|----------|:-:|---|
| Lựa chọn tài liệu | 9 / 10 | 10 tài liệu nguồn công khai thật, 9 khoá metadata, `sources.csv` khớp 1-1, provenance ghi rõ cả nguồn bị loại và lý do. Trừ 1 vì `document_version` toàn `not-stated` |
| Thiết kế chiến lược | 14 / 15 | 6 cấu hình đo được, giải thích được **vì sao** heading thắng, và có một kết luận bị chính số liệu bác bỏ rồi sửa lại. Trừ 1 vì mới 2/4 thành viên có số liệu |
| Chất lượng truy xuất | 8 / 10 | `heading` 8/10, 5/5 lọt top-3. Tự trừ vì 2 điểm của Q4 là phép đo suy biến |
| Thuyết trình | 4 / 5 | Có 4 phát hiện kèm số liệu, có ca lỗi tự chỉ ra. Trừ 1 vì chưa demo trước lớp |
| **Tổng phần nhóm** | **35 / 40** | |

---

## Còn thiếu — cần cả nhóm hoàn tất

**Nguyễn Tiến Đạt — sửa `_make_record` trong `src/store.py`.** Đổi
`meta["doc_id"] = doc.id` thành `meta.setdefault("doc_id", doc.id)`. Một dòng, và nó là khác
biệt giữa **0/10 và 8/10**. Nhóm cố ý **không** tự sửa: `src/` là phần chấm 30 điểm cá nhân
và báo cáo cá nhân của bạn phải mô tả đúng code của bạn.

**Phạm Thị Liên — sửa `delete_document` trong `src/store.py`.** Hiện chỉ so `record['id']`,
trong khi chunk từ `ingest` có id dạng `"<doc_id>::chunk_N"`, nên xoá 0 chunk và trả `False`
trên corpus thật. Cần khớp thêm `metadata['doc_id']`. Test không bắt được vì test dùng
`Document` có `id` trùng `doc_id`. (Lý do không tự sửa: như trên.)

**Cả ba — tự chạy benchmark trên máy mình** rồi commit CSV vào nhánh của mình:

```bash
python scripts/run_benchmark.py --chunker heading --max-chars 800
```

Bài tập 3.4 yêu cầu mỗi người tự chạy. Số liệu trong bảng trên là thật, nhưng do nhóm trưởng
chạy hộ bằng `git worktree` — đúng số liệu, sai quy trình.

**Cả nhóm — sửa Contract B thành `gold_doc_ids` dạng danh sách.** Q3 và Q5 có đáp án ở hai
tài liệu; hệ thống đưa nội dung đúng lên hạng 2 mà máy chấm vẫn cho 1 điểm thay vì 2. Sửa
xong thì `heading` lên **10/10**. Đây là lỗi thước đo, không phải lỗi hệ thống.