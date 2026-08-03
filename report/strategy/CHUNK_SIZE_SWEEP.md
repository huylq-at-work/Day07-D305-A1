# Quét `chunk_size` cho RecursiveChunker — Bài tập 3.1 Bước 2

> Chạy: `python scripts/sweep_chunk_size.py --sizes 300 500 800`
> Corpus `data/k3_university` (10 tài liệu), embedder
> `paraphrase-multilingual-MiniLM-L12-v2`, 5 câu hỏi trong `data/benchmark_queries.yaml`
> (đã có bộ lọc `institution`). Số liệu thô: [`chunk_size_sweep.json`](chunk_size_sweep.json).

## Hai chỉ số, và vì sao cần cả hai

| Chỉ số | Nghĩa | Điểm yếu |
| :-- | :-- | :-- |
| `rank_doc` | Hạng của **tài liệu** gold — đúng thứ rubric chấm | Hỏng khi đáp án nằm ở nhiều tài liệu (Q3, Q5) |
| `rank_needle` | Hạng của **chunk thực sự chứa câu trả lời**, dò bằng chuỗi mốc | Không phụ thuộc nhãn → dùng để so tham số |

## Kết quả

| chunk_size | số chunk | dài TB | **rubric** | `rank_needle` TB |
| --: | --: | --: | :-: | --: |
| 300 | 836 | 217.1 | **6/10** | 41.2 |
| 500 | 456 | 399.7 | **6/10** | 20.0 |
| 800 | 267 | 684.0 | **6/10** | 11.2 |

Chi tiết `rank_needle` từng câu:

| # | 300 | 500 | 800 |
| :-: | --: | --: | --: |
| Q1 | 112 | 71 | **45** |
| Q2 | **1** | 2 | 3 |
| Q3 | 84 | 21 | **2** |
| Q4 | 4 | 4 | **3** |
| Q5 | 5 | **2** | 3 |

## Phát hiện 1 — Chỉ số của rubric không phân biệt được tham số

**Cả ba cấu hình đều ra đúng 6/10**, dù số chunk chênh nhau hơn 3 lần (836 so với 267).
Chọn tham số theo điểm rubric là chọn bằng tung đồng xu.

Tệ hơn: ba cấu hình đạt 6 điểm bằng **ba đường khác nhau**. Ở 800, Q3 lên hạng 2 (được 1
điểm) nhưng Q1 tụt từ hạng 1 xuống 2 (mất 1 điểm) — tổng bù trừ vừa đúng bằng nhau. Nhìn
mỗi con số 6/10 thì không thấy gì đang xảy ra bên dưới.

`rank_needle` thì phân biệt rõ và đơn điệu: **41.2 → 20.0 → 11.2**. Chunk lớn hơn kéo đoạn
chứa câu trả lời lên hạng cao hơn, chủ yếu vì số chunk cạnh tranh giảm đi.

## Phát hiện 2 — `chunk_size=800` bị mô hình cắt cụt âm thầm

Đây là lý do **không** chọn 800 dù nó có `rank_needle` tốt nhất.

`paraphrase-multilingual-MiniLM-L12-v2` có `max_seq_length = 128 token`. Đo thực tế:

| chunk_size | Token (tiếng Việt) | Token (tiếng Anh) | Trong giới hạn? |
| --: | --: | --: | :-- |
| 300 | 68 | 55 | có |
| 500 | **112** | 90 | có, sát trần |
| 800 | **176** | 144 | **KHÔNG — bị cắt** |

Ở 800, khoảng **30–40% cuối mỗi chunk không hề đi vào vector**. Điều nguy hiểm là nó không
báo lỗi: `store` vẫn lưu và trả về **nguyên văn** chunk 800 ký tự, nhưng vector đại diện chỉ
mô tả phần đầu. Câu trả lời nằm ở đuôi chunk thì **truy xuất không bao giờ tìm ra**, dù
đoạn văn đó có mặt trong kho.

Tiếng Việt chạm trần sớm hơn tiếng Anh: cùng 800 ký tự cho **176 token tiếng Việt** so với
144 token tiếng Anh, vì tokenizer đa ngữ cắt tiếng Việt thành nhiều mảnh con hơn. Corpus
này có 4/10 tài liệu tiếng Việt nên bất lợi đó là thật, không phải giả định.

Suy ra ngân sách an toàn: 128 token ≈ **550 ký tự tiếng Việt**, ≈ 700 ký tự tiếng Anh.

## Phát hiện 3 — `rank_doc = 1` không có nghĩa là agent đọc được câu trả lời

Q1 là ca rõ nhất. Ở `chunk_size=500`, `rank_doc = 1` (được 2 điểm rubric) nhưng
`rank_needle = 71`. Nghĩa là tài liệu đúng lên hạng 1 **nhờ một chunk khác**, còn đoạn chứa
"18-22 credits" nằm tận hạng 71 — ngoài top-3 rất xa.

Đây chính là lời giải thích cho việc tác tử trả lời sai Q1 trong
[`ANSWERS.md`](../benchmark/ANSWERS.md) dù rubric cho 2 điểm: **top-3 không hề chứa câu trả
lời**, agent chỉ có ba chunk cùng tài liệu nhưng nói chuyện khác.

Rubric chấm ở mức tài liệu, còn agent đọc ở mức chunk. Hai mức đó lệch nhau, và `rank_doc`
che mất khoảng lệch ấy.

## Kết luận: chọn `chunk_size = 500`

| Ứng viên | Vì sao loại / chọn |
| :-- | :-- |
| 300 | `rank_needle` tệ nhất (41.2). 836 chunk quá vụn, mỗi chunk ~217 ký tự thiếu ngữ cảnh và cạnh tranh lẫn nhau |
| **500** | **Chọn.** 112 token — sát trần 128 mà không vượt, tận dụng gần hết năng lực mô hình. `rank_needle` 20.0, tốt hơn 300 gấp đôi |
| 800 | `rank_needle` tốt nhất nhưng **đạt được trên vector cắt cụt**. Con số 11.2 không phản ánh chunk 800 ký tự, nó phản ánh ~550 ký tự đầu cộng với việc pool nhỏ đi |

Nói cách khác, 800 "thắng" phần lớn vì **giảm số đối thủ**, không phải vì chunk giàu thông
tin hơn. Muốn hưởng lợi thế đó một cách trung thực thì phải đổi sang mô hình có
`max_seq_length` lớn hơn, chứ không phải tăng `chunk_size` vượt trần rồi coi như không biết.

## Việc còn thiếu

- **Chưa quét bộ separator.** Mới chỉ thử `chunk_size`; `["\n\n", "\n", ". ", " ", ""]` vẫn
  là mặc định. Với văn bản quy định, thêm `"\nĐiều "` hoặc `"\nArticle "` vào đầu danh sách
  có thể bám ranh giới điều khoản tốt hơn — đáng thử ở vòng sau.
- **Q4 vẫn là phép đo suy biến.** Lọc `institution=ueh` để lại pool 40/23/13 chunk từ **một**
  tài liệu, nên `rank_doc = 1` gần như cho không ở cả ba cấu hình.
- **Chưa sửa `gold_doc_id` của Q3 và Q5.** Hai câu này vẫn bị chấm sai ở mọi `chunk_size`;
  xem [FAILURE_ANALYSIS](../benchmark/FAILURE_ANALYSIS.md) đề xuất số 2.
