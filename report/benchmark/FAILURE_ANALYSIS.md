# Phân tích lỗi — Bài tập 3.5

> Lần chạy: `recursive`, `chunk_size=500`, 456 chunk / 10 tài liệu,
> `paraphrase-multilingual-MiniLM-L12-v2`. Số liệu:
> [`01821-LeQuangHuy_recursive.csv`](01821-LeQuangHuy_recursive.csv).

## Kết quả trần trụi: 0/10

| # | kind | rank_of_gold | Tài liệu hạng 1 thực tế |
| :-: | :-- | --: | :-- |
| Q1 | fact | 7 | `ueh-dang-ky-huy-hoc-phan` |
| Q2 | filtered | 5 | `ou-quy-che-hoc-vu-tin-chi` |
| Q3 | multi_doc | 6 | `vinuni-academic-regulations-undergrad` |
| Q4 | paraphrase | 8 | `vnuf-huong-dan-quy-che-tin-chi` |
| Q5 | edge | **99** | `vinuni-academic-regulations-undergrad` |

Không câu nào lọt top-3. Nhưng "0 điểm" gộp chung **ba nguyên nhân khác hẳn nhau**, và
một trong ba là lỗi thiết kế benchmark của chính tôi. Ba thí nghiệm dưới đây tách chúng ra.

---

## Nguyên nhân 1 — Khoảng cách xuyên ngữ ở cấp CHUNK (nặng nhất)

Câu hỏi tiếng Việt, đoạn văn chứa đáp án tiếng Anh. Giữ nguyên chunk vàng
(`18-22 credits`), chỉ đổi ngôn ngữ câu hỏi:

| Hỏi bằng | Điểm chunk vàng | Hạng |
| :-- | --: | --: |
| Tiếng Việt | 0.4641 | **192/456** |
| Tiếng Anh | 0.5827 | **19/456** |

Cùng một chunk, cùng một corpus, chỉ đổi ngôn ngữ hỏi → hạng cải thiện **10 lần**.

Điều này **mâu thuẫn với dự đoán tôi ghi ở Bài tập 3.3**. Ở đó cặp P2 (câu hỏi tiếng Việt
vs câu tiếng Anh cùng nghĩa) đạt 0.77, và tôi kết luận "corpus trộn vi/en là an toàn".
Kết luận đó **sai**, và sai vì phép thử không đại diện:

- P2 so **hai câu ngắn dịch sát nghĩa nhau** — trường hợp thuận lợi nhất cho mô hình đa ngữ.
- Thực tế benchmark là so **một câu hỏi ngắn tiếng Việt** với **một khối 500 ký tự tiếng
  Anh** chứa cả bảng biểu, tiêu đề Article, và nhiều ý không liên quan.

Bài học rút ra: đo độ tương tự trên cặp câu sạch **không dự đoán được** hành vi trên chunk
thật. Muốn biết retrieval hoạt động ra sao thì phải đo trên chính chunk sẽ dùng.

---

## Nguyên nhân 2 — Nhiễu đa trường (thật, nhưng không phải thủ phạm chính)

Corpus gồm 5 trường. Câu hỏi có ghi "VinUni" nhưng embedding không đánh trọng số cho tên
trường — nó chỉ thấy "sinh viên", "tín chỉ", "học kỳ". Bỏ 4 trường kia, chỉ giữ 250 chunk
VinUni:

| # | Toàn corpus (456) | Chỉ VinUni (250) |
| :-: | --: | --: |
| Q1 | hạng 192 | hạng 71 |
| Q2 | hạng 7 | **hạng 2** |
| Q3 | hạng 32 | hạng 21 |
| Q5 | hạng 3 | **hạng 2** |

Cải thiện thật nhưng **không cứu được Q1** (71/250 vẫn trượt xa). Nghĩa là nhiễu đa trường
là yếu tố phụ; gỡ nó ra thì Q2 và Q5 vào top-3, còn Q1 vẫn hỏng vì nguyên nhân 1.

---

## Nguyên nhân 3 — Khoảng cách diễn đạt (Q4)

Q4 hỏi tiếng Việt, đáp án cũng tiếng Việt — không có yếu tố ngôn ngữ. Giữ nguyên chunk
vàng, chỉ đổi cách diễn đạt câu hỏi:

| Cách hỏi | Điểm | Hạng |
| :-- | --: | --: |
| "chưa kịp **nộp tiền học** thì có bị **mất môn** không?" | 0.5063 | **63/456** |
| "không **đóng học phí** trong thời gian quy định thì học phần đã đăng ký có bị **hủy** không?" | 0.7521 | **9/456** |

Chỉ cần dùng đúng từ của văn bản là hạng nhảy từ 63 lên 9. Mô hình **không** bắc được cầu
giữa "nộp tiền học" và "đóng học phí", giữa "mất môn" và "hủy học phần" — dù người Việt
nào cũng hiểu đó là một.

Đây là dự đoán duy nhất tôi ghi trước mà đúng: ở Bài tập 3.3 tôi đã viết *"Q4 lấy được
đúng tài liệu nhưng rank_of_gold không phải 1"*. Thực tế còn tệ hơn — hạng 63.

---

## Nguyên nhân 4 — Nhãn `gold_doc_id` của Q5 đặt sai (lỗi của tôi)

Q5 hiện `rank_of_gold = 99`, trông như trượt hoàn toàn. Thực tế **retrieval đã làm đúng**:

```
3. 0.6311  vinuni-academic-regulations-undergrad
   "After returning from a temporary leave of absence, students must complete and
    submit a return application to the Office of Registrar, at least one week before
    the start of the new semester..."
```

Đoạn chứa câu trả lời nằm ở **hạng 3** — đủ ăn 1 điểm. Nhưng tôi gán
`gold_doc_id: vinuni-leave-of-absence`, trong khi mốc "một tuần" nằm ở
`vinuni-academic-regulations-undergrad`. Máy chấm so `doc_id` nên báo trượt.

Điều trớ trêu: Q5 được thiết kế để phơi bày **mâu thuẫn giữa hai tài liệu** (1 tuần vs 1
tháng). Chính vì đáp án nằm ở hai chỗ mà một trường `gold_doc_id` duy nhất là không đủ để
mô tả. **Contract B thiếu một trường `gold_doc_ids` dạng danh sách** — đây là khiếm khuyết
của thiết kế benchmark, không phải của hệ thống truy xuất.

---

## Đề xuất cải thiện, theo thứ tự đáng làm

| # | Việc | Cơ sở từ số liệu | Chi phí |
| :-: | :-- | :-- | :-- |
| 1 | **Thêm metadata `institution` + lọc theo nó** | Thí nghiệm 2: Q2 7→2, Q5 3→2 | Thấp — sửa front matter |
| 2 | **Sửa Contract B: `gold_doc_id` → `gold_doc_ids` (danh sách)** | Q5 bị chấm sai hoàn toàn | Thấp |
| 3 | **Corpus một ngôn ngữ, hoặc dịch câu hỏi sang ngôn ngữ tài liệu** | Thí nghiệm 1: hạng 192→19 | Trung bình |
| 4 | Đính tiêu đề mục vào đầu mỗi chunk | Chunk hạng 1 của Q3/Q5 là đoạn lạc ngữ cảnh | Trung bình — cần `HeadingChunker` của R2 |
| 5 | Mở rộng truy vấn (thêm từ đồng nghĩa hành chính) | Thí nghiệm 3: hạng 63→9 khi đổi từ | Cao |

Việc số 1 và 2 rẻ và tác động rõ — nên làm trước khi cả nhóm chạy benchmark, nếu không cả
bốn người sẽ cùng nhận 0 điểm vì cùng ba nguyên nhân này.

---

## Vòng 2 — áp dụng đề xuất số 1: thêm `institution` và lọc theo nó

Đổi **đúng một biến**: thêm trường `institution` vào front matter cả 10 tài liệu, và thêm
nó vào `metadata_filter` của cả 5 câu hỏi. Corpus, chunker, embedder, câu hỏi, gold answer
đều giữ nguyên. Số liệu vòng 1 lưu ở
[`01821-LeQuangHuy_recursive_v1-khong-loc-institution.csv`](01821-LeQuangHuy_recursive_v1-khong-loc-institution.csv).

| # | rank v1 | rank v2 | điểm v1 → v2 |
| :-: | --: | --: | :-- |
| Q1 | 7 | **1** | 0 → 2 |
| Q2 | 5 | **1** | 0 → 2 |
| Q3 | 6 | 6 | 0 → 0 |
| Q4 | 8 | **1** | 0 → 2 |
| Q5 | 99 | 5 | 0 → 0 |
| | | | **0/10 → 6/10** |

### Nhưng 2 trong 6 điểm đó không đáng tin

Kích thước pool sau khi lọc:

| institution | chunk | tài liệu |
| :-- | --: | --: |
| vinuni | 250 | 6 |
| vnuf | 95 | 1 |
| ou | 81 | 1 |
| **ueh** | **23** | **1** |
| iuh | 7 | 1 |

Q4 lọc `institution=ueh`, mà UEH chỉ có **đúng một tài liệu**. `rank_of_gold` đo ở mức tài
liệu, nên khi pool chỉ còn một tài liệu thì hạng 1 gần như **được cho không** — chỉ cần
trả về bất kỳ chunk nào là trúng. Hai điểm của Q4 không chứng minh được truy xuất tốt; nó
chỉ chứng minh bộ lọc đã thu hẹp bài toán đến mức tầm thường.

Đây là cái bẫy của chính chỉ số: `rank_of_gold` giả định pool đủ lớn để việc xếp đúng hạng
là thành tựu. Vòng 1 pool là 456 chunk / 10 tài liệu; vòng 2 với Q4 chỉ còn 23 chunk / 1
tài liệu. So hai con số đó với nhau như thể cùng thang đo là sai.

**Điểm thật đáng tin: Q1 và Q2 (4/10).** Cả hai lọc `institution=vinuni`, pool còn 250
chunk / 6 tài liệu — vẫn là bài toán thật, và cả hai nhảy từ trượt lên hạng 1. Đây là bằng
chứng sạch cho luận điểm: **thứ embedding không phân biệt được thì metadata phân biệt được.**

### Hai câu còn trượt đều cùng một nguyên nhân

Q3 (hạng 6) và Q5 (hạng 5) đều lọc `institution=vinuni`, và ở cả hai, tài liệu đứng hạng 1
là `vinuni-academic-regulations-undergrad` — **không phải** `gold_doc_id` tôi khai, nhưng
lại là tài liệu **có chứa câu trả lời**:

- Q3: trần 50% xuất hiện ở cả `vinuni-credit-transfer` (mục 3.2) lẫn acad-reg (Article 13).
- Q5: mốc "một tuần" nằm trong acad-reg, còn "một tháng" nằm trong `vinuni-leave-of-absence`.

Cả hai là câu hỏi có đáp án nằm ở **nhiều tài liệu**, trong khi Contract B chỉ cho khai
**một** `gold_doc_id`. Máy chấm so đúng một chuỗi nên báo trượt dù truy xuất đã đưa nội dung
đúng lên hạng 1. Đây là lỗi của thước đo, không phải của hệ thống — và là lý do đề xuất số
2 (`gold_doc_id` → `gold_doc_ids` dạng danh sách) nên làm ở vòng sau.

### Bài học về phương pháp

Nếu vòng 2 sửa cùng lúc cả `institution` lẫn nhãn gold thì 0/10 → 8/10 sẽ trông rất đẹp mà
**không giải thích được phần nào đến từ đâu**. Đổi một biến mỗi vòng khiến con số nhỏ hơn
nhưng nói được nhiều hơn.

---

## Điều đáng nói nhất

Con số 0/10 **không** có nghĩa là `EmbeddingStore` sai. 42/42 test pass, và smoke test cho
thấy `search_with_filter` loại đúng tài liệu `audience=faculty`. Cái hỏng nằm ở **thiết kế
dữ liệu và câu hỏi**, không nằm ở mã nguồn:

- Trộn hai ngôn ngữ trong khi hỏi bằng một ngôn ngữ → nguyên nhân 1.
- Trộn 5 trường trong khi hỏi về một trường → nguyên nhân 2.
- Hỏi bằng từ đời thường trong khi văn bản viết bằng từ hành chính → nguyên nhân 3.
- Một câu hỏi có đáp án ở hai tài liệu nhưng chỉ khai được một `gold_doc_id` → nguyên nhân 4.

Đúng như rubric nói: **chiến lược 15 điểm, hiệu suất 10 điểm**. Một lần chạy 0/10 giải
thích được bằng bốn thí nghiệm có kiểm soát đáng giá hơn một lần chạy 8/10 không lý giải nổi.
