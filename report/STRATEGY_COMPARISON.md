# So sánh chiến lược trong nhóm — REPORT_NHOM.md §2

> Cùng corpus `data/k3_university` (10 tài liệu), cùng 5 câu hỏi trong
> `data/benchmark_queries.yaml` (đã có bộ lọc `institution`), cùng embedder
> `paraphrase-multilingual-MiniLM-L12-v2`. Chỉ đổi **chiến lược chunking**.
>
> `HeadingChunker` là của Nguyễn Chí Hướng
> ([`scripts/custom_chunkers.py`](../scripts/custom_chunkers.py)); các cấu hình còn lại chạy
> bằng `RecursiveChunker` trong `src/chunking.py`.

## Kết quả

| Chiến lược | số chunk | dài TB | top-3 trúng | **điểm** | rank từng câu (Q1→Q5) |
| :-- | --: | --: | :-: | :-: | :-- |
| `recursive` 300 | 836 | 217 | 3/5 | 6/10 | 1, 1, 9, 1, 99 |
| `recursive` 500 | 456 | 400 | 3/5 | 6/10 | 1, 1, 6, 1, 5 |
| `recursive` 800 | 267 | 684 | 3/5 | 6/10 | 2, 1, 2, 1, 9 |
| `heading` max_chars=550 | 462 | 424 | 5/5 | 7/10 | 2, 1, 3, 1, 3 |
| `heading` max_chars=1200 | 217 | 860 | 5/5 | 7/10 | 2, 1, 3, 1, 2 |
| **`heading` max_chars=800** | **318** | **599** | **5/5** | **8/10** | **1, 1, 2, 1, 2** |

`HeadingChunker` thắng rõ: **5/5 câu lọt top-3** ở cả ba cấu hình, trong khi `recursive`
chỉ đạt 3/5 ở mọi `chunk_size`. Hai câu `recursive` luôn trượt — Q3 và Q5 — chính là hai
câu `heading` kéo được lên hạng 2.

## Vì sao heading thắng

Không phải vì chunk to hơn hay nhỏ hơn. `recursive` 800 và `heading` 800 có kích thước gần
nhau (684 so với 599 ký tự) nhưng chênh 2 điểm và chênh 2 câu top-3.

Khác biệt nằm ở **chỗ đặt nhát cắt**. `RecursiveChunker` cắt theo `\n\n` → `\n` → `. `,
tức theo hình thức trình bày. `HeadingChunker` cắt theo `Điều`, `Chương`, `Article`,
`Section` — ranh giới do **người soạn văn bản** đặt ra, nên mỗi chunk là một đơn vị quy định
trọn vẹn.

Chi tiết quyết định nhất nằm ở `_split_long_section`: khi một mục dài quá `max_chars`,
bạn Hướng **đính lại tiêu đề vào từng mảnh con**:

```python
return [f"{heading}\n\n{piece}".strip() for piece in body_chunks]
```

Chunk đứng một mình lúc được truy xuất thì không còn ngữ cảnh xung quanh; tiêu đề là mẩu
ngữ cảnh rẻ nhất có thể đính vào. Đây đúng là cải tiến số 4 trong
[FAILURE_ANALYSIS](benchmark/FAILURE_ANALYSIS.md) mà tôi đề xuất nhưng chưa làm.

## Một kết quả bác bỏ dự đoán của tôi

Trong [CHUNK_SIZE_SWEEP](strategy/CHUNK_SIZE_SWEEP.md) tôi kết luận nên tránh chunk vượt
trần 128 token của mô hình, vì phần đuôi bị cắt âm thầm. Đo lại trên `HeadingChunker`:

| max_chars | chunk bị cắt cụt | điểm |
| --: | :-- | :-: |
| 550 | 67/462 (14%) | 7/10 |
| **800** | **210/318 (66%)** | **8/10** |
| 1200 | 174/217 (80%) | 7/10 |

Cấu hình **tốt nhất lại là cấu hình có 66% số chunk bị cắt cụt**. Nghịch lý này có lời giải:
`HeadingChunker` đặt tiêu đề ở **đầu** mỗi chunk, mà cắt cụt thì cắt phần **đuôi** — nên
thông tin định danh quan trọng nhất (đây là Điều mấy, nói về cái gì) **luôn sống sót**.

Nói cách khác: vượt trần token không nguy hiểm bằng việc **để phần quan trọng nằm ở đuôi**.
Kết luận cũ của tôi ("giữ chunk dưới 550 ký tự") đúng với `RecursiveChunker`, nhưng không
áp dụng được cho chunker biết đặt tiêu đề lên đầu.

## Hai câu vẫn không đạt 2 điểm

Q3 và Q5 dừng ở hạng 2 với mọi cấu hình. Cả hai đều có tài liệu hạng 1 là
`vinuni-academic-regulations-undergrad` — **không phải** `gold_doc_id` khai trong file câu
hỏi, nhưng lại là tài liệu **có chứa câu trả lời**. Đây là giới hạn của thước đo, không phải
của chiến lược: Contract B chỉ cho khai một `gold_doc_id` trong khi đáp án nằm ở hai tài
liệu. Sửa thành `gold_doc_ids` dạng danh sách thì cả hai lên 2 điểm và tổng thành 10/10.

## Việc còn lại của nhóm

Bảng trên mới có **một người chạy** (tất cả do nhánh `01821-LeQuangHuy` chạy). Theo Bài tập
3.4, mỗi thành viên phải tự chạy 5 câu hỏi bằng `src/` **của mình** rồi nộp CSV theo
Contract C. Ba bạn còn lại đều đã pass 42/42 nên chạy được ngay:

```bash
python scripts/run_benchmark.py --chunker heading --max-chars 800
```

Bốn file CSV cùng 11 cột mới gộp được thành `ALL.csv` — lúc đó bảng so sánh mới là so sánh
**giữa các thành viên**, chứ không phải so sánh giữa các tham số như bảng hiện tại.
