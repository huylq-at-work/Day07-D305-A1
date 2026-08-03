# PLAN — Day 07 (K3): Embedding & Vector Store

> Tài liệu này là kế hoạch tổng cho cả nhóm. Mỗi role đọc thêm file riêng trong
> [`roles/`](roles/). Phân công và quy trình git ở [TEAMMATES.md](../TEAMMATES.md).
> Định dạng đầu ra bắt buộc giữa các role ở [CONTRACTS.md](CONTRACTS.md) — đọc trước khi
> sản xuất bất kỳ dữ liệu nào.

## 1. Mục tiêu bài lab

Đây **không phải** bài "làm cái chatbot trả lời được câu hỏi". Đây là bài **chứng minh
bằng số liệu rằng chiến lược chunking + metadata quyết định chất lượng truy xuất**.

Vòng lặp trung tâm của Giai đoạn 2:

1. Nhóm chốt **một** bộ tài liệu và **năm** câu hỏi đánh giá kèm gold answer.
2. Mỗi người nạp cùng bộ tài liệu đó bằng **chiến lược chunking khác nhau**.
3. Chạy cùng 5 câu hỏi, ghi lại top-3 của từng câu.
4. Đặt cạnh nhau: chiến lược nào thắng ở câu nào, và **vì sao**.
5. Tìm ít nhất một trường hợp truy xuất **thất bại**, giải thích nguyên nhân.

Rubric nói thẳng: **chiến lược (15đ) > hiệu suất (10đ)**. Nhóm giải thích được vì sao
chiến lược A thắng B sẽ hơn nhóm có điểm truy xuất cao mà không lý giải được.

## 2. Trạng thái hiện tại

| Hạng mục | Trạng thái |
| :-- | :-- |
| `.venv` (Python 3.11) | ❌ Mỗi người tự tạo trên máy mình |
| `src/chunking.py`, `src/store.py`, `src/agent.py` | ⚠️ 15 TODO — **mỗi người tự làm**, không chia |
| `Document` + `FixedSizeChunker` | ✅ Đã cho sẵn làm ví dụ |
| `ingest.py` (pipeline nạp dữ liệu) | ✅ Đã cho sẵn — **không phải viết lại** |
| `tests/test_solution.py` | ✅ 42 test — phần lớn FAIL đến khi làm xong TODO |
| `data/k3_university/` | ⚠️ Chỉ có 2 file mồi + `sources.csv` mẫu — cần 5–10 tài liệu thật |
| `data/benchmark_queries.yaml` | ❌ Chưa có — R3 tạo |
| `scripts/run_benchmark.py` | ❌ Chưa có — R3 viết |
| `report/REPORT_NHOM.md` | ⚠️ Template rỗng |
| `report/REPORT_CANHAN.md` | ⚠️ Template rỗng — mỗi người một bản |

**Việc chặn cả nhóm:** chưa có corpus thật và chưa chốt 5 câu hỏi. Không có hai thứ đó thì
không ai chạy được benchmark, và ba trong bốn mục của báo cáo nhóm trống. Đây là việc đầu tiên.

## 3. Hai cái bẫy có sẵn trong đề

**Bẫy 1 — chạy benchmark bằng mock embedder.** Mặc định lab dùng `_mock_embed`. Nó sinh
vector xác định nhưng **gần như ngẫu nhiên theo chuỗi**: đủ để pass unit test, nhưng điểm
tương đồng **không phản ánh ngữ nghĩa**. Kết luận "chiến lược A tốt hơn B" rút ra từ mock là
kết luận từ nhiễu. Giai đoạn 2 **bắt buộc** đặt trong `.env`:

```text
EMBEDDING_PROVIDER=local
```

và cài `pip install -r requirements-local.txt`. Lần chạy đầu sẽ tải model
`paraphrase-multilingual-MiniLM-L12-v2` — làm sớm, đừng để đến lúc chạy benchmark mới tải.

**Bẫy 2 — bốn người chạy trên bốn bộ dữ liệu hơi khác nhau.** Chỉ cần một người thêm tài
liệu hoặc sửa front matter giữa chừng là bảng so sánh mất ý nghĩa, mà khi đọc report thì
không nhìn ra. Cơ chế chống: corpus freeze và query freeze ở mục 5, do R1 và R3 tuyên bố.

## 4. Deliverable bắt buộc

| # | Deliverable | Owner | Mốc |
| :-: | :-- | :-- | :-- |
| 1 | `.venv` Python 3.11 + `pytest` chạy được (dù FAIL) | Cả nhóm | Giờ 1 |
| 2 | Corpus 5–10 tài liệu K3 + front matter đầy đủ + `sources.csv` | R1 | Giờ 1 |
| 3 | Metadata schema chốt (có `audience` + ≥2 trường hữu ích) | R1 | Giờ 1 |
| 4 | Mỗi người pass **42/42** `pytest tests/ -v` | Cá nhân | Giờ 2 |
| 5 | 5 câu hỏi + gold answer, ≥1 câu cần `metadata_filter` | R3 | Giờ 2 |
| 6 | `scripts/run_benchmark.py` chạy được | R3 | Giờ 2 |
| 7 | Baseline `ChunkingStrategyComparator().compare()` trên 2–3 tài liệu | R2 | Giờ 2 |
| 8 | Mỗi người chạy 5 câu hỏi bằng chiến lược của mình, nộp top-3 | Cá nhân | Giờ 3 |
| 9 | Bảng so sánh chéo 4 chiến lược | R2 | Giờ 3 |
| 10 | Phân tích ≥1 failure case | R3 + R2 | Giờ 3 |
| 11 | `REPORT_NHOM.md` hoàn chỉnh 4 phần | R4 ráp | Giờ 4 |
| 12 | Demo: chiến lược + so sánh + bài học | R4 dẫn | Giờ 4 |
| 13 | `REPORT_CANHAN_<MSSV>.md` của từng người | Cá nhân | Giờ 4 |

## 5. Timeline theo checkpoint

Mốc giờ dưới đây là tương đối — chỉnh theo lịch buổi lab thực tế của lớp.

```text
Giờ 1  Kickoff + Data      — đọc TEAMMATES.md, tạo branch, chốt chiến lược mỗi người
                             R1 crawl corpus; cả nhóm dựng .venv + cài local embedder
                          → CORPUS FREEZE (R1 tuyên bố trong nhóm chat)
Giờ 2  Code + Query        — mỗi người làm TODO tới khi pass 42 test
                             R3 viết 5 câu hỏi + harness; R2 chạy baseline comparator
                          → QUERY FREEZE (R3 tuyên bố)
Giờ 3  Benchmark           — cả 4 chạy cùng 5 câu hỏi, mỗi người một chiến lược
                             R2 gom bảng so sánh; R3 chấm theo rubric 2đ/câu
                             R2 + R3 chốt failure case
Giờ 4  Report + Demo       — R4 ráp REPORT_NHOM; mỗi người viết REPORT_CANHAN
                             Demo với nhóm khác, ghi lại phản biện
```

## 6. Đường găng và rủi ro

**Đường găng là R1 (corpus).** Ba deliverable lớn — bảng so sánh, điểm truy xuất, failure
analysis — đều nằm sau corpus freeze. Nếu hết Giờ 1 mà chưa có đủ tài liệu, nhóm chốt tạm
với số tài liệu đang có (tối thiểu 5) và **freeze luôn**, còn hơn để cả nhóm ngồi chờ.

**Rủi ro 2 — TODO cá nhân chưa xong thì không benchmark được.** `run_benchmark.py` gọi
`EmbeddingStore.search()` và `search_with_filter()`; ai chưa pass test thì chưa chạy được
gì ở Giờ 3. Ưu tiên làm `store.py` trước `agent.py`: benchmark cần store, chỉ mục "câu trả
lời của agent" mới cần agent.

**Rủi ro 3 — model local tải chậm.** Lần đầu `LocalEmbedder()` tải cả PyTorch lẫn model.
Chạy lệnh smoke test ngay Giờ 1, đừng đợi tới Giờ 3:

```bash
python -c "from src import LocalEmbedder; e=LocalEmbedder(); print(e._backend_name, len(e('test')))"
```

Nếu in ra tên backend mock nghĩa là fallback đã kích hoạt — thiếu thư viện hoặc sai
`EMBEDDING_PROVIDER`. Fallback im lặng là cái bẫy khó thấy nhất trong lab này.

**Rủi ro 4 — so sánh không công bằng.** Nếu người A dùng `chunk_size=200` còn người B dùng
`chunk_size=800` thì khác biệt có thể chỉ đến từ số chunk chứ không phải chiến lược. Khi so
sánh, luôn ghi kèm **số chunk** và **độ dài chunk trung bình** (đây chính là output của
`ChunkingStrategyComparator.compare()`).

## 7. Điều kiện một kết quả benchmark được dùng làm bằng chứng

- Chạy sau **corpus freeze** và **query freeze**, trên `main` đã pull mới nhất.
- `EMBEDDING_PROVIDER=local`, và đã xác nhận `_backend_name` **không** phải mock.
- `store.get_collection_size()` khớp giữa các thành viên về **số tài liệu** (số chunk khác
  nhau là bình thường — đó chính là điều đang đo).
- Cả 42 test pass trên `src/` của người chạy. Store sai thì mọi số phía sau đều vô nghĩa.

Ba con số phải ghi lại cho mỗi lần chạy: **số chunk**, **điểm số của top-1**, và **rank của
chunk chứa gold answer**. Rank là con số nói lên nhiều nhất; "có trong top-3" và "đứng
top-1" là hai chất lượng khác nhau, và rubric chấm khác nhau (2đ so với 1đ).

## 8. Lệnh dùng chung (Windows PowerShell)

Tất cả lệnh chạy từ gốc repo.

Tạo môi trường (Python 3.11 là chuẩn của lab):

```bash
py -3.11 -m venv .venv
```

Kích hoạt:

```bash
.venv\Scripts\Activate.ps1
```

Cài thư viện bắt buộc + embedder local cho Giai đoạn 2:

```bash
pip install -r requirements.txt -r requirements-local.txt
```

Chạy test (mục tiêu 42/42):

```bash
pytest tests/ -v
```

Kiểm tra pipeline nạp dữ liệu mà chưa cần store xong:

```bash
python ingest.py
```

Chạy demo thủ công:

```bash
python main.py
```

Chạy benchmark của nhóm (script do R3 viết):

```bash
python scripts\run_benchmark.py --chunker heading --top-k 3
```

**Lưu ý:** `.env` được `main.py` tự nạp; với snippet chạy trực tiếp thì gọi `load_dotenv()`
hoặc set biến môi trường trong shell. Không commit `.env`.

## 9. Bản đồ file

| Path | Ai sở hữu | Mục đích |
| :-- | :-- | :-- |
| `src/**` | **Mỗi người bản riêng** | 15 TODO — 30 điểm cá nhân, không merge lên `main` |
| `data/k3_university/**` | R1 | corpus K3, front matter, `sources.csv` |
| `scripts/fetch_public_pages.py` | R1 | crawl trang công khai |
| `scripts/custom_chunkers.py` | R2 | `HeadingChunker` + chunker tùy chỉnh |
| `scripts/compare_strategies.py` | R2 | chạy comparator, xuất bảng baseline |
| `data/benchmark_queries.yaml` | R3 | 5 câu hỏi + gold answer (freeze) |
| `scripts/run_benchmark.py` | R3 | harness chạy 5 câu hỏi, in top-3 |
| `report/strategy/` | R2 | output bảng so sánh chiến lược |
| `report/benchmark/` | R3 | kết quả top-3 của từng thành viên |
| `docs/CONTRACTS.md` | R4 | định dạng đầu ra bắt buộc — chốt Giờ 1 |
| `scripts/merge_benchmark.py` | R4 | gộp 4 CSV -> `report/benchmark/ALL.csv` |
| `report/REPORT_NHOM.md` | R4 ráp, cả nhóm viết | nộp 1 bản/nhóm — 40 điểm |
| `report/REPORT_CANHAN_<MSSV>.md` | Cá nhân | nộp 1 bản/người — 60 điểm |
| `ingest.py` | **Không ai sửa** | pipeline đã cho sẵn |
| `tests/test_solution.py` | **Không ai sửa** | 42 test chấm điểm |
