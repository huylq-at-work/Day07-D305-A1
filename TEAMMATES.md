# DANH SÁCH THÀNH VIÊN NHÓM

> Day 07 — K3: Nền tảng Dữ liệu, Embedding & Vector Store · Đại học VinUni
> Repo: `Day07-D305-A1` · Thư mục làm việc: gốc repo

## 1. Thành viên

| STT | Họ và tên | Mã sinh viên |
| :-: | :-- | :-- |
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

## 2. Phân công vai trò & Branch

Bài lab này chia làm hai giai đoạn với tính chất **ngược nhau**, nên đọc kỹ trước khi chia việc:

- **Giai đoạn 1 (60 điểm, cá nhân)** — **không chia được**. Mỗi người phải tự hoàn thành
  toàn bộ TODO trong `src/chunking.py`, `src/store.py`, `src/agent.py` trên máy mình. Chép
  code của nhau là mất 30/60 điểm cá nhân. Bốn vai dưới đây **không** phân chia phần này.
- **Giai đoạn 2 (40 điểm, nhóm)** — chia được, và đó là toàn bộ mục đích của bảng dưới.

Repo không có sẵn role docs; bốn vai dưới đây do nhóm tự định nghĩa, chia theo **file sở
hữu** để không conflict và để mỗi mục trong `REPORT_NHOM.md` có đúng một người chịu trách nhiệm.

| Thành viên | Vai trò | Branch | File sở hữu (chỉ người này được sửa) | Hướng dẫn |
| :-- | :-- | :-- | :-- | :-- |
| | Data Curator & Metadata Owner | `role1-data-curator` | `data/k3_university/**`, `data/k3_university/sources.csv`, `scripts/fetch_public_pages.py`, `scripts/urls.csv` | [ROLE1](docs/roles/ROLE1_DATA_CURATOR.md) |
| | Chunking Strategy Lead (heading/section) | `role2-strategy-lead` | `scripts/compare_strategies.py`, `scripts/custom_chunkers.py`, `report/strategy/` | [ROLE2](docs/roles/ROLE2_STRATEGY_LEAD.md) |
| | Benchmark & Evaluation Designer | `role3-benchmark-eval` | `data/benchmark_queries.yaml`, `scripts/run_benchmark.py`, `report/benchmark/` | [ROLE3](docs/roles/ROLE3_BENCHMARK_EVAL.md) |
| *(trưởng nhóm)* | Integrator, Report & Demo Lead | `role4-report-demo` | `docs/CONTRACTS.md`, `scripts/merge_benchmark.py`, `report/REPORT_NHOM.md`, `docs/plan.md`, `TEAMMATES.md` | [ROLE4](docs/roles/ROLE4_REPORT_DEMO.md) |

Kế hoạch tổng theo mốc thời gian: [docs/plan.md](docs/plan.md)
Định dạng đầu ra bắt buộc giữa các role: [docs/CONTRACTS.md](docs/CONTRACTS.md)

### Đầu ra của bốn người ghép vào nhau như thế nào

R4 chốt [docs/CONTRACTS.md](docs/CONTRACTS.md) **ngay Giờ 1**, trước khi ai sản xuất dữ
liệu. Bốn contract đó là chỗ nối:

```text
R1  corpus + front matter 7 khóa      ──┐
                                         ├──> ingest.build_knowledge_base(...)
R3  5 câu hỏi + gold_doc_id           ──┘         │
                                                   ▼
mỗi người chạy run_benchmark.py bằng CHIẾN LƯỢC RIÊNG
                                                   │
                        4 file CSV cùng 11 cột (Contract C)
                                                   ▼
                     R4: merge_benchmark.py -> report/benchmark/ALL.csv
                                                   │
                 ┌─────────────────┬───────────────┴──────────────┐
              R2 bảng so sánh   R3 chấm 10đ                 R4 ráp REPORT_NHOM
                 (§2, 15đ)      + failure (§3, 10đ)          (§4 + bản cuối)
```

Điểm mấu chốt: **không ai gõ lại số của ai**. Bốn người nộp bốn CSV cùng bộ cột, `ALL.csv`
là nguồn duy nhất cho mọi bảng trong báo cáo. Bốn người làm đúng theo bốn định dạng khác
nhau là cách hỏng phổ biến hơn nhiều so với ai đó làm sai — và nó chỉ lộ ra ở Giờ 4.

### Quy tắc sở hữu file — đọc kỹ

**`src/` là của riêng từng người, không bao giờ merge vào `main`.** Mỗi người giữ bản `src/`
của mình trên branch riêng. Đây không phải sự cứng nhắc: rubric chấm 30 điểm cho việc
*bạn* pass `pytest tests/ -v`, và Phần 2 báo cáo cá nhân bắt bạn giải thích **cách bạn viết**
từng hàm. Merge `src/` chung là tự xóa phần khác biệt giữa bốn báo cáo cá nhân.

**Chỉ R1 được sửa `data/k3_university/`.** Bốn người chạy benchmark trên **cùng một bộ tài
liệu**; nếu giữa chừng có người thêm/sửa file dữ liệu thì kết quả top-3 của người chạy trước
và người chạy sau không so sánh được với nhau, và cả bảng so sánh chiến lược ở Phần 2 mất giá
trị. Cần thêm tài liệu thì báo R1, R1 sửa và thông báo "corpus freeze" lại cho cả nhóm.

**Không ai sửa `data/benchmark_queries.yaml` sau khi đã freeze** — kể cả R3. Sửa câu hỏi
giữa chừng là lý do phổ biến nhất khiến bảng so sánh của bốn người không cộng lại được.

**Mỗi người chọn một chiến lược chunking KHÁC nhau.** Đây là yêu cầu của đề (Bài tập 3.1),
không phải gợi ý. Chốt trong 15 phút đầu, ghi vào bảng ở mục 3 bên dưới. Riêng K3 bắt buộc
**ít nhất một người** chunk theo tiêu đề/mục (heading/section) — mặc định giao cho R2.

### Chiến lược của từng người (chốt ở Kickoff)

| Thành viên | Chiến lược | Tham số dự kiến |
| :-- | :-- | :-- |
| | `FixedSizeChunker` (tuned) | `chunk_size=`, `overlap=` |
| | `HeadingChunker` (custom, theo mục của quy định) | — |
| | `SentenceChunker` (tuned) | `max_sentences_per_chunk=` |
| | `RecursiveChunker` (tuned) | `separators=`, `chunk_size=` |

## 3. Quy trình Git

Tạo bốn branch trước khi bắt đầu. **Không ai commit thẳng vào `main`** — mọi thay đổi vào
`main` phải đi qua Pull Request và được R4 review.

| Branch | Người dùng |
| :-- | :-- |
| `role1-data-curator` | |
| `role2-strategy-lead` | |
| `role3-benchmark-eval` | |
| `role4-report-demo` | |

**Tạo branch (lần đầu, mỗi người chạy trên máy mình):**

```bash
git fetch origin && git checkout -b role1-data-curator && git push -u origin HEAD
```

*(đổi tên branch theo bảng trên)*

**Trong lúc làm — lấy code mới nhất từ main vào branch của mình:**

```bash
git pull origin main
```

**Làm xong — đẩy lên branch của mình:**

```bash
git add . && git commit -m "Role X: mo ta ngan" && git push origin HEAD
```

**Mở Pull Request:**

```bash
gh pr create --base main --head role1-data-curator --title "Role 1: corpus K3 + metadata schema" --body "5-10 tai lieu, front matter day du, sources.csv"
```

**R4 review và merge:**

```bash
gh pr list && gh pr merge <số PR> --merge --delete-branch=false
```

Giữ branch lại (`--delete-branch=false`) vì mỗi người còn dùng tiếp cho vòng sau.

### Thứ tự merge bắt buộc

Ba người sau đều chạy trên bộ tài liệu của R1 và bộ câu hỏi của R3, nên thứ tự là:

1. PR của **R1** (corpus + `sources.csv` + metadata schema) merge vào `main` **trước**.
   Từ lúc này corpus **freeze**.
2. PR của **R3** (`benchmark_queries.yaml` + `run_benchmark.py`) merge tiếp. Câu hỏi **freeze**.
3. Cả bốn người `git pull origin main`, rồi mới chạy benchmark bằng `src/` của mình.
   Chạy trước bước này thì số liệu không so sánh chéo được.
4. **R2** tổng hợp bảng so sánh, **R4** ráp báo cáo.

### Xử lý conflict

Bảng sở hữu file ở mục 2 được thiết kế để **không có conflict** — đặc biệt là việc `src/`
không bao giờ lên `main`. Nếu vẫn conflict, nghĩa là ai đó đã sửa file không thuộc phần
mình: dừng lại, hỏi trong nhóm, đừng tự resolve. File hay bị đụng nhất là
`report/REPORT_NHOM.md` vì cả nhóm cùng viết; quy ước: mỗi người chỉ sửa đúng mục của mình
(xem bảng ở [ROLE4](docs/roles/ROLE4_REPORT_DEMO.md)), và pull `main` ngay trước khi viết.

### Báo cáo cá nhân

`report/REPORT_CANHAN.md` là **một file cho mỗi sinh viên**. Mỗi người giữ bản của mình
trên branch riêng, đặt tên `report/REPORT_CANHAN_<MSSV>.md` khi nộp để không ghi đè nhau.
Không merge file này vào `main`.

## 4. Không commit

`.env`, API key dưới mọi dạng, `.venv/`, `__pycache__/`, model cache của
`sentence-transformers`, và bất kỳ tài liệu nào có dữ liệu cá nhân / thông tin đăng nhập /
hồ sơ nội bộ (xem quy tắc dữ liệu bắt buộc trong [docs/DATA_COLLECTION.md](docs/DATA_COLLECTION.md)).
Kiểm tra bằng `git status` trước mỗi lần commit.
