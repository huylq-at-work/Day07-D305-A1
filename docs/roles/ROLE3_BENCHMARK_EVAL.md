# ROLE 3 — Benchmark & Evaluation Designer

**Người phụ trách:** *(chưa điền)* · **Branch:** `role3-benchmark-eval`

> Đọc [docs/plan.md](../plan.md) và [docs/CONTRACTS.md](../CONTRACTS.md) trước.
> Mọi lệnh chạy từ gốc repo.

## Bạn sở hữu

- `data/benchmark_queries.yaml` — 5 câu hỏi + gold answer
- `scripts/run_benchmark.py` — harness cả nhóm dùng chung
- `report/benchmark/` — nơi bốn người nộp CSV kết quả

Bạn định nghĩa **thước đo**. Ba người kia thi trên thước của bạn, nên thước sai thì toàn bộ
số liệu của nhóm sai theo mà không ai phát hiện được.

## Bạn không được làm

- Không sửa `data/k3_university/` — của R1. Câu hỏi phải bám dữ liệu có thật; thấy thiếu
  tài liệu để hỏi thì **yêu cầu R1 bổ sung**, đừng tự thêm file.
- Không sửa `benchmark_queries.yaml` sau khi tuyên bố QUERY FREEZE — kể cả bạn. Sửa câu hỏi
  khi đã có người chạy là cách chắc chắn nhất để bảng so sánh mất giá trị.
- Không viết gold answer bằng kiến thức chung về "các trường thường quy định thế nào". Gold
  answer phải **trích được từ tài liệu nhóm thu thập** — yêu cầu ghi thẳng trong `K3_VARIANT.md`.

## Nhiệm vụ

### T1 — Viết 5 câu hỏi (Bài tập 3.2)

Đúng 5 câu, theo [Contract B](../CONTRACTS.md#2-contract-b--bộ-câu-hỏi-đánh-giá). Ba ràng
buộc của đề, kiểm từng cái:

1. **Đa dạng** — không được 5 câu cùng một khuôn. Trường `kind` tồn tại để ép việc này:
   `fact` (một chi tiết trong một tài liệu), `filtered` (cần lọc metadata), `multi_doc`
   (thông tin nằm ở hai tài liệu), `paraphrase` (dùng từ khác hẳn tài liệu),
   `edge` (trường hợp ngoại lệ, con số ít gặp).
2. **Gold answer cụ thể, kiểm chứng được** — có số, có ngày, có điều kiện. "Sinh viên được
   gia hạn theo quy định" không phải gold answer. "Tối đa 2 lần, mỗi lần 7 ngày, nếu sách
   không có người đặt trước" mới là.
3. **≥1 câu cần `metadata_filter`** — yêu cầu riêng K3, thường là
   `{"audience": "student"}`. Câu này chỉ có giá trị khi corpus của R1 **thật sự có** tài
   liệu `audience` khác trả lời cùng chủ đề. Không có tài liệu mồi thì bộ lọc không lọc đi
   cái gì, và cả câu hỏi lẫn 10 điểm chất lượng truy xuất mất chỗ chứng minh. Kiểm với R1
   trước khi chốt.

Câu `paraphrase` là câu đáng đầu tư nhất: hỏi bằng từ ngữ sinh viên thật dùng ("bị phạt bao
nhiêu nếu trả sách muộn") trong khi tài liệu viết theo văn phong hành chính ("mức thu đối
với trường hợp quá hạn hoàn trả"). Đó chính là chỗ embedding chứng minh nó hơn tìm kiếm từ
khóa — hoặc chỗ nó gãy, mà cả hai kết quả đều đáng viết.

### T2 — Viết `scripts/run_benchmark.py`

Harness dùng chung. Yêu cầu tối thiểu:

```bash
python scripts\run_benchmark.py --chunker heading --top-k 3
```

Luồng xử lý:

1. Đọc `data/benchmark_queries.yaml`.
2. Gọi `build_knowledge_base("data/k3_university", embedding_fn, chunker=<chọn theo --chunker>)`
   trong `ingest.py`. **Không viết lại pipeline này** — đề đã cho sẵn.
3. Với mỗi câu: gọi `store.search()`, hoặc `store.search_with_filter()` khi câu có
   `metadata_filter`.
4. Tìm vị trí đầu tiên có `metadata["doc_id"] == gold_doc_id` → `rank_of_gold`
   (không thấy trong top-10 thì ghi `99`).
5. Ghi CSV đúng 11 cột của [Contract C](../CONTRACTS.md#3-contract-c--bảng-kết-quả-benchmark-quan-trọng-nhất).

Hai điều harness phải tự kiểm và **dừng lại nếu sai**, vì đây là hai lỗi im lặng đắt nhất
của lab này:

- **Embedder là mock.** In `_backend_name` ra đầu output. Chạy benchmark bằng
  `_mock_embed` cho ra điểm gần như ngẫu nhiên, trông vẫn "có kết quả", và mọi kết luận rút
  ra từ đó đều sai.
- **Collection rỗng hoặc thiếu tài liệu.** In `store.get_collection_size()` và số `doc_id`
  phân biệt được. Front matter hỏng ở một file sẽ làm mất metadata của cả file đó mà không
  ném exception.

`rubric_score` để harness chấm tự động phần retrieval (2 nếu `rank_of_gold == 1`, 1 nếu
`<= 3`, 0 nếu không), rồi người chạy tự hạ xuống 1 nếu câu trả lời của agent thiếu chi tiết
so với gold. Ghi rõ quy ước này trong `--help` để bốn người chấm giống nhau.

### T3 — Tuyên bố QUERY FREEZE

Khi 5 câu đã chốt và harness chạy được trên máy bạn: mở PR, R4 merge, rồi nhắn trong nhóm.
Từ đó cả bốn người mới chạy. Freeze phải xảy ra **sau** CORPUS FREEZE của R1 — chạy trước
thì `gold_doc_id` có thể trỏ vào tài liệu chưa tồn tại.

### T4 — Chạy phần của mình + chấm cả nhóm

Chạy 5 câu bằng chiến lược của riêng bạn, nộp CSV theo Contract C.

Sau khi R4 gộp `ALL.csv`, bạn chấm **10 điểm Chất lượng Truy xuất** theo `docs/SCORING.md`
(2 điểm/câu). Kiểm lại thủ công vài dòng `rubric_score` do harness tự chấm: máy chỉ biết
gold **doc** có trong top-3, nó không biết chunk được truy xuất có thật sự **chứa** câu trả
lời hay chỉ tình cờ cùng tài liệu. Đúng doc nhưng sai mục là ca thường gặp, và nó nên bị hạ
xuống 1 điểm.

### T5 — Phân tích lỗi (Bài tập 3.5)

Lọc `ALL.csv` lấy dòng `rubric_score == 0` hoặc `rank_of_gold` cao bất thường. Chọn **ít
nhất một** ca, viết theo ba câu hỏi của đề: câu hỏi nào trượt, **vì sao**, đề xuất sửa gì.

`top1_doc_id` là manh mối chính — nó cho biết hệ thống đã nhầm sang tài liệu nào, và loại
nhầm lẫn thường rơi vào một trong bốn nhóm:

| Triệu chứng | Nguyên nhân thường gặp | Hướng sửa |
| :-- | :-- | :-- |
| Đúng tài liệu, sai mục | chunk quá lớn, một chunk gộp nhiều điều khoản | giảm `chunk_size`, hoặc chunk theo heading |
| Trả về mẩu vụn không nội dung | chunk quá nhỏ, mất ngữ cảnh | tăng overlap, gộp mục ngắn |
| Nhầm sang tài liệu của `audience` khác | thiếu `metadata_filter` | thêm bộ lọc, hoặc đính `audience` vào text chunk |
| Từ ngữ câu hỏi khác hẳn tài liệu | giới hạn của embedding | đính tiêu đề mục vào chunk; ghi nhận là giới hạn thật |

Một ca trượt được giải thích đúng có giá trị hơn năm câu đều pass — rubric ưu tiên
**chiến lược 15đ trên hiệu suất 10đ**, và phân tích lỗi là nơi thể hiện điều đó rõ nhất.

## Tiêu chí hoàn thành

- [ ] `data/benchmark_queries.yaml` đúng 5 câu, đủ trường theo Contract B
- [ ] 5 câu **không trùng `kind` hết**; có ≥1 câu `metadata_filter` khác `null`
- [ ] Mọi `gold_answer` trích được từ tài liệu thật, mọi `gold_doc_id` tồn tại trong corpus
- [ ] Đã xác nhận với R1 rằng câu `filtered` có tài liệu mồi để lọc ra
- [ ] `run_benchmark.py` in `_backend_name` + `get_collection_size()`, dừng nếu embedder là mock
- [ ] CSV xuất ra đúng 11 cột, đúng thứ tự Contract C
- [ ] Đã tuyên bố QUERY FREEZE sau CORPUS FREEZE
- [ ] Đã chấm 10 điểm retrieval cho cả nhóm và soát tay ít nhất 5 dòng
- [ ] ≥1 failure case viết đủ ba phần: câu nào, vì sao, sửa thế nào

## Bàn giao

- Cho **cả nhóm**: `run_benchmark.py` + hướng dẫn một dòng để chạy, ngay sau QUERY FREEZE.
- Cho **R2**: các ca trượt, để R2 đối chiếu với đặc điểm chunk của từng chiến lược.
- Cho **R4**: mục 3 của `REPORT_NHOM.md` (Câu hỏi đánh giá & Chất lượng truy xuất) và phần
  phân tích lỗi cho mục 4.
