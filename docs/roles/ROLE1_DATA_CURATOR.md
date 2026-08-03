# ROLE 1 — Data Curator & Metadata Owner

**Người phụ trách:** *(chưa điền)* · **Branch:** `role1-data-curator`

> Đọc [docs/plan.md](../plan.md) và [docs/CONTRACTS.md](../CONTRACTS.md) trước.
> Mọi lệnh chạy từ gốc repo.

## Bạn sở hữu

- `data/k3_university/**` — toàn bộ corpus
- `data/k3_university/sources.csv`
- `scripts/fetch_public_pages.py`, `scripts/urls.csv`

Bạn là **người duy nhất** được sửa thư mục `data/k3_university/`. Lý do ở
[TEAMMATES.md](../../TEAMMATES.md) mục 2: ba người còn lại chạy benchmark trên corpus của
bạn, corpus đổi giữa chừng thì số liệu của người chạy trước và chạy sau không so được.

## Bạn không được làm

- Không sửa `data/benchmark_queries.yaml` — của R3. Bạn thấy câu hỏi không trả lời được từ
  corpus thì **báo R3**, đừng tự sửa câu hỏi cho khớp dữ liệu.
- Không đổi corpus sau khi đã tuyên bố CORPUS FREEZE. Cần thêm tài liệu thì phải hủy freeze
  công khai và báo ai đã chạy rồi phải chạy lại.
- Không tự bịa `document_version` hay `retrieved_at` cho đẹp bảng. Không biết thì ghi
  `unknown` — rubric chấm "nguồn minh bạch", không chấm "bảng đầy".

## Nhiệm vụ

### T1 — Khoanh phạm vi (15 phút đầu)

Chủ đề K3 **cố định**: dịch vụ / quy định đại học. Chọn **một** lát cắt hẹp thay vì rải đều
năm lĩnh vực:

| Lát cắt | Ví dụ tài liệu |
| :-- | :-- |
| Học vụ | quy chế đăng ký học phần, rút môn, học lại, xét tốt nghiệp |
| Tài chính | mức học phí, hạn nộp, phí trễ hạn, chính sách miễn giảm |
| Học bổng | điều kiện xét, hồ sơ, thời hạn, mức học bổng |
| Thư viện | mượn/trả/gia hạn, phạt quá hạn, truy cập tài nguyên số |
| Ký túc xá | điều kiện ở, phí, nội quy, quy trình đăng ký |

Chọn hẹp có lý do thực tế: 5 câu hỏi đánh giá của R3 phải phân biệt được tài liệu này với
tài liệu kia. Corpus rải năm lĩnh vực thì câu nào cũng dễ, retrieval trông giỏi hơn thực tế
và phần phân tích lỗi không có gì để nói. Corpus tập trung một lĩnh vực mới tạo ra **các
tài liệu gần giống nhau** — đó mới là chỗ chiến lược chunking bộc lộ khác biệt.

Nên giữ **1–2 tài liệu dành cho `audience` khác** (`faculty` hoặc `staff`) nói về cùng chủ
đề. Đây là mồi cho câu hỏi cần `metadata_filter` của R3: không có nó thì bộ lọc metadata
lọc ra đúng thứ đã có sẵn, và cả yêu cầu K3 lẫn 15 điểm thiết kế chiến lược mất chỗ chứng minh.

### T2 — Thu thập 5–10 tài liệu

Đọc [docs/DATA_COLLECTION.md](../DATA_COLLECTION.md) trước khi crawl. Chỉ dùng nguồn công
khai hoặc nguồn nhóm có quyền dùng.

Có sẵn script crawl trang công khai:

```bash
python scripts\fetch_public_pages.py --input scripts\urls.csv --output data\k3_university\
```

PDF thì chuyển sang Markdown:

```bash
pip install pymupdf4llm
```

Hoặc copy-paste thủ công — với 5–10 tài liệu thì thường nhanh hơn debug crawler.

**Làm sạch trước khi lưu:** bỏ menu, breadcrumb, footer, "bài viết liên quan". Rác điều
hướng lặp lại giống nhau ở mọi trang, và vì nó lặp lại nên embedding của các chunk chứa nó
sẽ giống nhau — chunk rác cạnh tranh trực tiếp với chunk nội dung ở top-3.

### T3 — Gắn front matter theo Contract A

Đủ **8 khóa** cho mọi file, đúng schema của hai file mồi: `doc_id`, `title`, `audience`,
`department`, `language`, `source_url`, `retrieved_at`, `document_version`. Chi tiết và quy
ước enum ở [CONTRACTS §1](../CONTRACTS.md#1-contract-a--front-matter-tài-liệu).

Hai file mồi (`course-registration.md`, `library-services.md`) đang dùng `source_url` giả
(`example.edu`) và `license_or_permission: example-template-replace-me`. Thay bằng nguồn
thật hoặc bỏ khỏi corpus — đây là mục bị soi trực tiếp ở tiêu chí "nguồn minh bạch".

Kiểm ngay sau khi gắn — lệnh này chạy được **trước khi** bạn làm xong TODO của `src`:

```bash
python ingest.py
```

Rồi kiểm từng file thật:

```bash
python -c "from ingest import load_documents; [print(d.id, sorted(d.metadata)) for d in load_documents('data/k3_university')]"
```

Mọi dòng in ra phải có đủ 8 khóa (cộng `source` do `load_documents` tự thêm). File nào
thiếu — hoặc tệ hơn, in ra danh sách khóa rỗng vì quên dòng `---` mở đầu — sửa ngay. Lỗi
front matter **không ném exception**, nó chỉ làm mọi bộ lọc metadata trượt im lặng ở Giờ 3.

### T4 — `sources.csv`

Giữ 7 cột sẵn có, thêm `char_count` ở cuối:
`doc_id,file_path,title,source_url,retrieved_at,document_version,license_or_permission,char_count`.
Lưu UTF-8 — bản mồi hiện đang hỏng mã tiếng Việt, ghi đè lại cả file.

`char_count` đếm phần thân, không tính front matter:

```bash
python -c "from ingest import load_documents; [print(d.id, len(d.content)) for d in load_documents('data/k3_university')]"
```

R2 cần cột này để giải thích chênh lệch số chunk giữa các chiến lược; thiếu nó thì bảng so
sánh chỉ còn là bảng số không diễn giải được.

### T5 — Tuyên bố CORPUS FREEZE

Khi đủ 5–10 tài liệu, front matter sạch, `sources.csv` khớp: mở PR, R4 merge, rồi **nhắn
trong nhóm** đúng một câu — corpus đã freeze, số tài liệu bao nhiêu, tổng số ký tự bao nhiêu.

Từ giây phút đó ba người kia mới bắt đầu chạy. Freeze muộn là rủi ro số một của cả nhóm
(xem [plan.md §6](../plan.md#6-đường-găng-và-rủi-ro)): hết Giờ 1 mà chưa đủ 10 tài liệu thì
**freeze với số đang có, tối thiểu 5**, còn hơn để ba người ngồi chờ.

### T6 — Viết Phần 1 của báo cáo nhóm

Bạn viết `report/REPORT_NHOM.md` **mục 1** (Lựa chọn tài liệu — 10 điểm): phạm vi, bảng
Data Inventory, metadata schema và lý do chọn từng trường. Chỉ sửa đúng mục 1, pull `main`
ngay trước khi viết.

Phần dễ mất điểm nhất là "lý do chọn trường metadata". Đừng liệt kê tên trường — nói **câu
hỏi nào cần đến nó**. Ví dụ: `audience` tồn tại để câu hỏi về học phí không trả về văn bản
hướng dẫn dành cho phòng đào tạo; `category` tồn tại để thu hẹp không gian tìm kiếm khi hai
lĩnh vực dùng chung từ vựng ("gia hạn" có cả ở thư viện lẫn học phí).

## Tiêu chí hoàn thành

- [ ] 5–10 tài liệu `.md` trong `data/k3_university/`, đã làm sạch rác điều hướng
- [ ] Mọi file có đủ 7 khóa front matter, `doc_id` trùng tên file
- [ ] `audience` và `category` dùng đúng enum, không có giá trị tiếng Việt lạc
- [ ] Có ≥1 tài liệu `audience` khác `student` để bộ lọc metadata có việc để làm
- [ ] `python ingest.py` chạy sạch; lệnh kiểm ở T3 in đủ khóa cho mọi tài liệu
- [ ] `sources.csv` đủ 8 cột, số dòng khớp số file
- [ ] Không có dữ liệu cá nhân / thông tin đăng nhập / hồ sơ nội bộ trong repo
- [ ] Đã tuyên bố CORPUS FREEZE trong nhóm

## Bàn giao

- Cho **R3**: danh sách `doc_id` + `title` + `audience`, để R3 viết `gold_doc_id` cho 5 câu
  hỏi. Nói rõ tài liệu nào là mồi cho câu cần `metadata_filter`.
- Cho **R2**: `sources.csv` (cột `char_count`) và gợi ý 2–3 tài liệu có cấu trúc khác nhau
  rõ rệt để chạy baseline comparator.
- Cho **R4**: mục 1 của `REPORT_NHOM.md` đã viết xong, và một câu tuyên bố freeze kèm số liệu.
