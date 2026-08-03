# ROLE 2 — Chunking Strategy Lead (heading/section)

**Người phụ trách:** Nguyễn Chí Hướng — K3 · **Member benchmark:** `01203_NguyenChiHuong`

> Nhánh Git cá nhân: `2A202601203-NguyenChiHuong`; các CSV cá nhân dùng member id
> `01203_NguyenChiHuong` để R4 ghép kết quả.

> Đọc [docs/plan.md](../plan.md) và [docs/CONTRACTS.md](../CONTRACTS.md) trước.
> Mọi lệnh chạy từ gốc repo.

## Bạn sở hữu

- `scripts/custom_chunkers.py` — `HeadingChunker` và mọi chunker tùy chỉnh của nhóm
- `scripts/compare_strategies.py` — chạy `ChunkingStrategyComparator`, xuất Contract D
- `report/strategy/` — output baseline + bảng so sánh chiến lược

Bạn nhận thêm một ràng buộc từ đề: **K3 bắt buộc ít nhất một thành viên chunk theo
tiêu đề/mục** của sổ tay hoặc quy định học vụ. Nhóm giao việc đó cho bạn.

## Bạn không được làm

- Không sửa `data/k3_university/` — của R1. Thấy tài liệu có cấu trúc heading hỏng thì báo
  R1 sửa, đừng tự sửa file dữ liệu để chunker của mình chạy đẹp hơn. Sửa dữ liệu cho vừa
  thuật toán là làm hỏng cơ sở so sánh của ba người kia.
- Không sửa `data/benchmark_queries.yaml` — của R3.
- Không sửa `src/` của người khác. `HeadingChunker` viết trong `scripts/custom_chunkers.py`,
  không nhét vào `src/chunking.py` — `src/` là bài nộp cá nhân, và `tests/test_solution.py`
  chỉ chấm ba chunker của đề.

## Nhiệm vụ

### T1 — Baseline comparator (Bài tập 3.1 Bước 1)

Chạy `ChunkingStrategyComparator().compare()` trên **2–3 tài liệu** do R1 chỉ định, chọn
tài liệu có cấu trúc khác nhau rõ rệt: một cái nhiều heading ngắn, một cái văn xuôi liền mạch.

```bash
python scripts\compare_strategies.py --docs data\k3_university --limit 3 --chunk-size 200
```

Ghi output theo [Contract D](../CONTRACTS.md#4-contract-d--kết-quả-baseline-comparator) vào
`report/strategy/baseline_<doc_id>.json`.

**Trước khi chạy, kiểm embedder.** Baseline chạy bằng mock là baseline vô nghĩa:

```bash
python -c "from src import LocalEmbedder; e=LocalEmbedder(); print(e._backend_name)"
```

In ra tên mock nghĩa là fallback đã kích hoạt im lặng — thiếu `requirements-local.txt` hoặc
sai `EMBEDDING_PROVIDER` trong `.env`. Sửa xong mới chạy lại.

Đọc kết quả theo ba con số, không chỉ nhìn "chiến lược nào nhiều chunk hơn": **số chunk**,
**độ dài chunk trung bình**, và **độ lệch độ dài**. Độ lệch lớn là dấu hiệu chiến lược đang
tạo ra vài chunk rất dài lẫn nhiều mẩu vụn — mẩu vụn hầu như không bao giờ lên top-3 nhưng
vẫn làm loãng collection.

### T2 — Viết `HeadingChunker`

Ý tưởng: quy định và sổ tay học vụ đã được người viết chia sẵn theo mục ("1. Phạm vi áp
dụng", "## Điều kiện gia hạn"). Ranh giới đó mang **ngữ nghĩa thật**, khác hẳn ranh giới
500 ký tự của `FixedSizeChunker` vốn cắt ngang giữa câu.

```python
class HeadingChunker:
    """Chia theo tiêu đề Markdown, giữ nguyên một mục làm một chunk.

    Lý do thiết kế: quy định học vụ được viết theo điều/khoản; một câu hỏi của
    sinh viên hầu như luôn được trả lời trọn vẹn trong đúng một mục.
    """

    def __init__(self, max_level: int = 2, max_chars: int = 1200) -> None:
        ...

    def chunk(self, text: str) -> list[str]:
        ...
```

Ba chỗ phải xử lý, và cũng là ba chỗ đáng viết vào báo cáo:

1. **Mục quá dài** (vượt `max_chars`): chia tiếp bên trong bằng `RecursiveChunker` thay vì
   trả về một chunk khổng lồ — chunk dài làm loãng embedding, điểm tương đồng tụt cho mọi truy vấn.
2. **Mục quá ngắn** (một dòng "## Ghi chú"): gộp với mục kế tiếp, đừng để chunk 20 ký tự.
3. **Phần mở đầu trước heading đầu tiên**: vẫn phải thành một chunk, đừng bỏ.

Cân nhắc **kèm tiêu đề vào đầu mỗi chunk** ("Điều 5. Gia hạn — <nội dung>"). Chunk đứng một
mình khi được truy xuất không còn ngữ cảnh xung quanh; tiêu đề là mẩu ngữ cảnh rẻ nhất bạn
có thể đính vào. Nếu thử cả hai biến thể, giữ số liệu của cả hai — đó là một đoạn so sánh
tốt cho mục 2 của báo cáo.

### T3 — So với baseline (Bài tập 3.1 Bước 3)

Chạy `HeadingChunker` **trên cùng những tài liệu** đã chạy ở T1, cùng embedder. Đặt cạnh
baseline: số chunk, độ dài trung bình, và — quan trọng hơn cả — **một ví dụ cụ thể** về một
chunk mà chiến lược cũ cắt hỏng còn chiến lược của bạn giữ nguyên. Một ví dụ đọc được
thuyết phục hơn ba dòng thống kê.

### T4 — Chạy 5 câu hỏi và nộp Contract C

Sau QUERY FREEZE, chạy harness của R3 bằng chunker của bạn:

```bash
python scripts\run_benchmark.py --chunker heading --top-k 3
```

Nộp `report/benchmark/01203_NguyenChiHuong_heading.csv` đúng 11 cột theo
[Contract C](../CONTRACTS.md#3-contract-c--bảng-kết-quả-benchmark-quan-trọng-nhất), 5 dòng,
kèm 3 dòng comment điều kiện hợp lệ ở đầu file.

### T5 — Bảng so sánh chéo bốn chiến lược

Sau khi cả bốn người nộp CSV, R4 gộp thành `report/benchmark/ALL.csv`. Bạn dựng bảng so sánh
cho **mục 2** của `REPORT_NHOM.md` từ file đó — pivot `rank_of_gold` theo `query_id` ×
`member_branch`, kèm cột `n_chunks_total`.

Ba câu hỏi rubric muốn nghe, trả lời bằng số trong bảng:

- Chiến lược nào truy xuất tốt nhất **tổng thể**, và tốt hơn bao nhiêu?
- Có câu hỏi nào **A thắng B nhưng câu khác thì ngược lại** không? Đây là câu đáng giá nhất
  — nó chứng minh không có chiến lược thắng tuyệt đối, và giải thích được vì sao thì gần như
  chắc chắn ăn trọn 15 điểm thiết kế chiến lược.
- Chênh lệch có đến từ **chiến lược** hay chỉ từ **số chunk**? Nếu `heading` tạo 143 chunk
  còn `fixed` tạo 512 chunk thì một phần khác biệt chỉ là quy mô. Nói thẳng điều này ra
  thay vì giấu — rubric chấm khả năng lý giải, không chấm việc chiến lược của bạn thắng.

## Tiêu chí hoàn thành

- [ ] `report/strategy/baseline_<doc_id>.json` cho 2–3 tài liệu, đúng Contract D
- [ ] Đã xác nhận `_backend_name` không phải mock trước mọi lần chạy
- [ ] `HeadingChunker` xử lý cả ba ca: mục dài, mục ngắn, phần trước heading đầu tiên
- [ ] Có ≥1 ví dụ đọc được về chunk mà baseline cắt hỏng, heading giữ nguyên
- [x] `report/benchmark/01203_NguyenChiHuong_heading.csv` đúng 11 cột, 5 dòng
- [x] Đã chạy đối chứng `01203_NguyenChiHuong_recursive.csv` trên cùng corpus/query/embedder
- [ ] Bảng so sánh chéo dựng từ `ALL.csv`, không gõ tay số của ai
- [ ] Trả lời được cả ba câu hỏi ở T5 bằng số liệu

## Bàn giao

- Cho **R3**: nhận xét chunk nào trông "khó truy xuất" — nguyên liệu cho phần failure analysis.
- Cho **R4**: mục 2 của `REPORT_NHOM.md` (Thiết kế chiến lược) và mã nguồn `HeadingChunker`
  để dán vào báo cáo.
- Cho **cả nhóm**: `params` chính xác bạn đã dùng, để không ai đoán lại khi đọc bảng.
