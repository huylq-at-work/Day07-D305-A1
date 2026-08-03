# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Tiến Đạt
**Nhóm:** A1
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector có hướng rất sát nhau trong không gian nhiều chiều, thể hiện hai đoạn văn bản có ý nghĩa (ngữ nghĩa) hoặc chủ đề rất giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A:"Con chó đang nằm ngủ trên ghế."
- Câu B:"Một chú cún con đang say giấc ngoài phòng khách."
- Tại sao tương đồng: Cả hai câu đều nói về một con chó đang ngủ.

**Ví dụ có độ tương tự THẤP:**
- Câu A:"Tôi gửi tiền tiết kiệm vào ngân hàng (bank)."
- Câu B:"Tôi ngồi câu cá bên bờ sông (bank)."
- Tại sao khác:Trùng mặt chữ (từ "bank" trong tiếng Anh) nhưng khác biệt hoàn toàn về ngữ nghĩa (tài chính vs địa lý).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm đến "hướng" (ngữ nghĩa) thay vì "độ dài" của vector, nên rất hiệu quả để so sánh các đoạn văn bản có độ dài ngắn khác nhau (ví dụ: so một câu query ngắn với một chunk tài liệu dài).

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính: ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450)
> Đáp án:23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số lượng chunk sẽ tăng lên. Ta muốn chồng chéo nhiều hơn để bảo toàn ngữ cảnh nằm ở ranh giới các khối, tránh việc một câu hoặc một ý quan trọng bị cắt làm đôi gây mất nghĩa.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
>  Tôi dùng regex positive lookbehind (?<=[.!?])\s+ để tách đoạn tại khoảng trắng nhưng vẫn giữ lại dấu câu ở cuối. Các ngoại lệ như câu rỗng (edge case) được lọc bỏ bằng lệnh .strip(), sau đó ghép các mảng nhỏ lại với nhau giới hạn bởi max_sentences_per_chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy cắt văn bản dựa trên độ ưu tiên của các dấu phân cách. Base case là khi chuỗi đã ngắn hơn chunk_size hoặc khi không còn separator. Ở mỗi bước, tôi dùng biến buffer để gom các mảnh nhỏ liền kề, phần nào vẫn quá dài mới tiếp tục gọi đệ quy xuống tầng dưới.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Dữ liệu được chuyển thành dict, chèn thêm doc_id vào metadata để truy vết, rồi lưu vào _store (in-memory). Khi tìm kiếm, tôi lấy query đọ với từng record qua phép tính dot product, gom thành danh sách kết quả rồi sort giảm dần theo điểm score để lấy top_k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi thực hiện quy trình "lọc trước, rank sau": duyệt mảng để lấy ra các record khớp metadata rồi mới đưa vào hàm tìm kiếm, tránh việc lấy top_k trước rồi mới lọc gây hụt kết quả. Hàm xóa đơn giản dùng list comprehension bỏ qua các record trùng doc_id.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tôi gọi hàm search để lấy kết quả, nối chúng thành context và đánh số thứ tự [1] (doc_id) để dễ grounding. Prompt được cấu trúc chặt chẽ gồm: lệnh điều hướng (instruction), context và câu hỏi (question), ép LLM chỉ trả lời dựa trên ngữ cảnh được cung cấp.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\VIN\LABS\Day07-D305-A1
plugins: anyio-4.13.0, langsmith-0.10.10, html-4.2.0, metadata-3.1.1
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.15s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

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
| 1 | Ở VinUni, sinh viên đại học chính quy được đăng ký tối đa bao nhiêu... | Khối lượng học tập tối thiểu mà mỗi sinh viên phải đăng ký... | 0.707 | Không (sai nguồn ou-quy-che) | [DEMO LLM] Context: [1] (ou-quy-che-hoc-vu-tin-chi::chunk_41)... |
| 2 | Sinh viên VinUni được rút (withdraw) một học phần đã đăng ký muộn nhất... | Thời gian bảo lưu các kết quả học tập của các môn học... | 0.703 | Không (sai nguồn ou-quy-che) | [DEMO LLM] Context: [1] (ou-quy-che-hoc-vu-tin-chi::chunk_79)... |
| 3 | Em muốn chuyển đổi tín chỉ đã học ở trường cũ sang VinUni... | Area of application These guidelines apply to all full-time students... | 0.640 | Có | [DEMO LLM] Context: [1] (vinuni-credit-transfer::chunk_1)... |
| 4 | Em đăng ký môn xong rồi mà chưa kịp nộp tiền học thì có bị mất môn... | Việc rút bớt học phần trong khối lượng học tập đó đăng ký chỉ được... | 0.680 | Không (sai nguồn vnuf) | [DEMO LLM] Context: [1] (vnuf-huong-dan-quy-che-tin-chi::chunk_35)... |
| 5 | Sau khi bảo lưu, sinh viên VinUni phải nộp đơn xin quay lại... | Application Procedures: Students need to petition for transfer... | 0.726 | Không (sai quy trình transfer) | [DEMO LLM] Context: [1] (vinuni-academic-regulations-undergrad::chunk_56)... |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5

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
