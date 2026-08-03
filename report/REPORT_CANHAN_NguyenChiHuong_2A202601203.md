# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Chí Hướng
**Nhóm:** A1 
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao, gần `1`, nghĩa là hai vector embedding có hướng gần nhau trong
> không gian vector. Với một embedder ngữ nghĩa tốt, điều này thường cho thấy hai đoạn văn
> có nội dung hoặc ý nghĩa tương tự, dù cách dùng từ có thể khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên được rút học phần đã đăng ký muộn nhất khi nào?
- Câu B: Hạn chót để sinh viên hủy một môn đã đăng ký là bao giờ?
- Tại sao tương đồng: Hai câu cùng hỏi thời hạn bỏ một học phần; “rút”/“hủy” và
  “muộn nhất”/“hạn chót” là các cách diễn đạt gần nghĩa.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Hạn nộp học phí học kỳ 1 là ngày nào?
- Câu B: Công thức nấu phở bò truyền thống của Hà Nội.
- Tại sao khác: Một câu thuộc quy định học vụ, câu còn lại thuộc ẩm thực; chúng không
  chia sẻ chủ đề hay mục đích thông tin.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào góc giữa hai vector nên ít bị ảnh hưởng bởi độ lớn vector, trong khi
> khoảng cách Euclid thay đổi theo cả hướng lẫn độ lớn. Với text embedding, hướng thường
> biểu diễn quan hệ ngữ nghĩa hữu ích hơn độ dài tuyệt đối của vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước trượt là `500 - 50 = 450`. Số chunk là
> `1 + ceil((10,000 - 500) / 450) = 1 + ceil(21.111...) = 23`.
>
> **Đáp án: 23 chunks.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Bước trượt giảm còn `500 - 100 = 400`, nên số chunk tăng thành
> `1 + ceil(9,500 / 400) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới chunk và
> giảm nguy cơ cắt mất một ý, đổi lại tốn thêm lưu trữ và phép tính embedding/search.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi trả về danh sách rỗng khi đầu vào không có nội dung, sau đó dùng regex
> `(?<=[.!?])(?:[ \t]+|\n+)` để tách tại khoảng trắng hoặc xuống dòng sau dấu kết câu nhưng
> vẫn giữ dấu câu. Các câu được `strip`, bỏ phần rỗng rồi ghép theo từng nhóm tối đa
> `max_sentences_per_chunk`; constructor ép tham số này tối thiểu bằng 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt các separator theo thứ tự ưu tiên, gom các mảnh liền nhau đến gần
> `chunk_size`, và chỉ đệ quy bằng separator tiếp theo khi một mảnh vẫn quá dài. Các base case
> gồm text rỗng, text đã đủ ngắn, hết separator hoặc gặp separator `""`; hai trường hợp cuối
> cắt cứng theo số ký tự để bảo đảm đệ quy luôn dừng.

**`compute_similarity` + `ChunkingStrategyComparator.compare`** — hướng tiếp cận:
> Cosine similarity được tính bằng tích vô hướng chia cho tích hai norm và trả `0.0` nếu một
> vector có norm bằng 0. Comparator chạy đúng ba chiến lược `fixed_size`, `by_sentences` và
> `recursive`, rồi trả số chunk, độ dài trung bình và chính danh sách chunk; text rỗng được
> xử lý riêng để không chia cho 0.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hóa thành một record có ID chunk duy nhất, nội dung, bản sao
> metadata chứa `doc_id`, và embedding; `add_documents` không tự chia chunk vì việc đó thuộc
> pipeline `ingest.py`. Khi tìm kiếm, query chỉ được embed một lần, điểm của từng record là
> dot product với query embedding, sau đó sắp xếp giảm dần và lấy tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc record trước khi xếp hạng và chỉ giữ record khớp tất cả cặp
> key/value trong metadata; khi filter là `None`, hàm dùng đúng đường tìm kiếm thông thường.
> `delete_document` tìm và xóa toàn bộ chunk có `metadata['doc_id']` khớp, trả `True` nếu có
> ít nhất một chunk bị xóa và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi store để lấy top-k chunk, đánh số từng chunk và đưa cả `doc_id`, nguồn cùng nội
> dung vào phần `Context` để có thể truy vết. Prompt yêu cầu chỉ trả lời dựa trên context và
> nói rõ khi thiếu thông tin, sau đó thêm câu hỏi và nhãn `Answer:` trước khi gọi `llm_fn`;
> nếu store không trả kết quả, agent thông báo thiếu ngữ cảnh mà không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ python -m pytest tests -v
============================= test session starts =============================
platform win32 -- Python 3.11.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Dell\OneDrive\Desktop\AITHUCCHIEN\LABS\Day07-D305-A1
collected 42 items

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

============================= 42 passed in 0.14s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi ghi dự đoán trước khi chạy rồi đo lại bằng backend local
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (vector 384 chiều), không dùng
API và không dùng `MockEmbedder`. Các phép đo đều gọi đúng `compute_similarity()` trong
`src/chunking.py` trên hai vector đã được model chuẩn hóa.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được rút học phần đã đăng ký muộn nhất khi nào? | Hạn chót để sinh viên hủy một môn đã đăng ký là bao giờ? | Cao (`0.85`) | `0.8650` | Có |
| 2 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ? | What is the maximum number of credits a student may register in one semester? | Cao (`0.75`) | `0.1671` | Không |
| 3 | Quy định về rút học phần đã đăng ký. | Quy định về chuyển đổi tín chỉ từ trường khác. | Trung bình (`0.55`) | `0.9056` | Không, cao hơn dự đoán |
| 4 | Sinh viên rút học phần đã đăng ký trong học kỳ. | Sinh viên rút tiền mặt tại cây ATM trong khuôn viên trường. | Thấp (`0.35`) | `0.4928` | Không, ở mức trung bình |
| 5 | Hạn nộp học phí học kỳ 1 là ngày nào? | Công thức nấu phở bò truyền thống của Hà Nội. | Thấp nhất (`0.05`) | `0.8869` | Không, cao bất thường |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 bất ngờ nhất: hai câu khác hẳn chủ đề vẫn đạt `0.8869`, trong khi cặp song ngữ cùng hỏi
> số tín chỉ chỉ đạt `0.1671`. Điều này cho thấy một điểm cosine cao chỉ là tín hiệu xếp hạng
> trong chính không gian của model, không tự nó chứng minh hai câu có cùng đáp án. Vì vậy khi
> benchmark tôi kiểm tra chuỗi bằng chứng trong từng chunk, không kết luận từ score hoặc
> `doc_id` đơn thuần.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

**Cấu hình đã chạy:** `HeadingChunker(max_level=2, max_chars=1200)`, 10 tài liệu, tổng cộng
`218` chunk, `top_k=3`, backend local
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Năm query lấy nguyên từ
`data/benchmark_queries.yaml`. Chỉ biến strategy là HeadingChunker; việc đọc front matter,
gắn metadata/`doc_id`/`chunk_index` và nạp store đều dùng lại `build_knowledge_base()` của
`ingest.py`. File query hiện vẫn ghi bản nháp, chưa QUERY FREEZE, nên đây là kết quả cá nhân
phục vụ CP5 và phân tích retrieval, chưa phải CSV benchmark chính thức của nhóm.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | VinUni được đăng ký tối đa bao nhiêu tín chỉ trong học kỳ chính? | `vnuf-huong-dan-quy-che-tin-chi` — Điều 10 về khối lượng học tập tối thiểu | `0.6936` | Không; sai trường, top-3 không có chuỗi `18–22 credits` | Context không đủ bằng chứng để trả lời giới hạn VinUni; không được suy đoán từ quy định VNUF/OU. |
| 2 | Được withdraw muộn nhất khi nào và tối đa bao nhiêu tín chỉ? | `ueh-dang-ky-huy-hoc-phan` — Chương IV về lớp học phần bị hủy | `0.6715` | Có trong top-3; chunk hạng 3 chứa đủ `30%` và `maximum of 18 credits` | Có thể trả lời: trước 30% thời lượng học phần và tổng số tín chỉ rút tối đa là 18; tuy nhiên bằng chứng không đứng top-1. |
| 3 | Chuyển tín chỉ từ trường cũ: tối đa bao nhiêu và nộp lúc nào? | `vinuni-academic-regulations-undergrad` — Điều 13 về chuyển tín chỉ | `0.7017` | Chưa đủ; top-3 có mốc `50%` nhưng thiếu chuỗi “during the first week of the semester” | Context chỉ đủ trả lời giới hạn 50%, chưa đủ căn cứ trả lời trọn vẹn thời điểm nộp. |
| 4 | Chưa nộp học phí thì có bị mất môn không? | `vnuf-huong-dan-quy-che-tin-chi` — quy định rút học phần tuần 6–8 | `0.6430` | Không; top-3 không có câu UEH “hủy học phần chưa đóng học phí” | Context sai trường và thiếu hậu quả cần trả lời, nên agent phải báo không đủ thông tin. |
| 5 | Sau bảo lưu phải xin quay lại trước bao lâu? | `vinuni-academic-regulations-undergrad` — Điều 13 về chuyển tín chỉ | `0.7349` | Không; gold document ở hạng 2 nhưng sai section, thiếu cả mốc 1 tháng và 1 tuần | Context không đủ để nêu hai quy định khác nhau; đúng `doc_id` ở một kết quả vẫn không bảo đảm đúng chunk. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5 theo tiêu chí nghiêm ngặt
“top-3 phải chứa đủ các chuỗi bằng chứng của gold answer”. Q2 đạt đủ hai marker nhưng ở hạng
3; Q3 chỉ đạt một trong hai marker. Nếu chỉ chấm theo `gold_doc_id`, tài liệu chuẩn xuất hiện
trong top-3 ở 3/5 câu (Q2, Q3, Q5). Chênh lệch `3/5` theo document và `1/5` theo chunk chứng
minh rằng đánh giá theo `doc_id` có thể lạc quan hơn chất lượng retrieval thực tế.

**A/B metadata filter:** Q2 được chạy hai lần với cùng query, corpus, embedder và strategy.
Khi có `metadata_filter={"audience": "student"}`, top-3 lần lượt là UEH, VinUni và VinUni;
chunk VinUni hạng 3 chứa đủ đáp án. Khi bỏ filter, top-3 đổi thành hai chunk VNUF và một chunk
UEH, không còn chunk đáp án VinUni. Như vậy filter thực sự giảm nhiễu giữa các quy định học vụ
có từ vựng gần nhau và là điều kiện cần để Q2 trả lời đúng đối tượng.

**Failure case tiêu biểu — Q5:** top-3 có đúng `vinuni-leave-of-absence` ở hạng 2, score
`0.6310`, nhưng đó là section thủ tục không chứa mốc “at least one month before”; top-1 lại là
section chuyển tín chỉ của tài liệu khác. Nguyên nhân không phải “model sai” chung chung mà là
các section VinUni có chủ đề gần nhau, trong khi heading chunk không overlap nên điều khoản
thời hạn chỉ có một cơ hội lọt top-k. Thay đổi đề xuất: gắn heading cha vào mọi mảnh recursive,
thêm overlap nhỏ cho section dài và cân nhắc rerank theo marker/metadata sau bước cosine.

**Giới hạn phần trả lời:** máy không có API LLM nên benchmark này dùng `demo_llm` để kiểm tra
prompt/provenance, còn embedding là model local thật. Vì `demo_llm` chỉ trả preview prompt,
tôi chấm retrieval dựa trên bằng chứng trong chunk và không tuyên bố đã đo chất lượng sinh câu
trả lời của một LLM.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng benchmark tốt phải có nhiều kiểu câu hỏi và gold answer kiểm chứng được,
> không chỉ vài câu chứa đúng từ khóa của tài liệu. Đặc biệt Q5 của nhóm cho thấy lấy đúng
> document vẫn chưa đủ: chunk phải chứa đúng điều khoản và agent phải nêu được mâu thuẫn giữa
> hai nguồn thay vì chọn tùy ý một mốc thời gian.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |
