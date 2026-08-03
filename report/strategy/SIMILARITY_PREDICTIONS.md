# Bài tập 3.3 — Dự đoán độ tương tự cosine

> **Viết TRƯỚC khi chạy `compute_similarity()`.** Cột "Thực tế" để trống cho tới khi chạy
> xong; commit này cố định phần dự đoán để không sửa lùi sau khi thấy kết quả.
>
> Embedder: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`EMBEDDING_PROVIDER=local`).
> Năm cặp câu lấy trong miền học vụ của corpus [`data/hoc-vu-01821/`](../../data/hoc-vu-01821).

## Năm cặp câu

| # | Câu A | Câu B | Điều đang thử |
| :-: | :-- | :-- | :-- |
| P1 | Sinh viên được rút học phần đã đăng ký muộn nhất khi nào? | Hạn chót để sinh viên hủy một môn đã đăng ký là bao giờ? | Cùng nghĩa, cùng tiếng Việt, **khác từ vựng** ("rút" vs "hủy", "muộn nhất" vs "hạn chót") |
| P2 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ? | What is the maximum number of credits a student may register in one semester? | Cùng nghĩa, **khác ngôn ngữ** — phép thử đa ngữ |
| P3 | Quy định về rút học phần đã đăng ký. | Quy định về chuyển đổi tín chỉ từ trường khác. | Cùng miền học vụ, **khác chủ đề** |
| P4 | Sinh viên rút học phần đã đăng ký trong học kỳ. | Sinh viên rút tiền mặt tại cây ATM trong khuôn viên trường. | **Bẫy từ vựng**: trùng "sinh viên", "rút", "trường" nhưng khác nghĩa hoàn toàn |
| P5 | Hạn nộp học phí học kỳ 1 là ngày nào? | Công thức nấu phở bò truyền thống của Hà Nội. | Không liên quan gì — đường đáy |

## Dự đoán

| # | Dự đoán | Thực tế | Lệch | Lý do dự đoán |
| :-: | --: | --: | --: | :-- |
| P1 | **0.85** | | | Cùng nghĩa, cùng ngôn ngữ, cùng cấu trúc câu hỏi. Model được huấn luyện cho paraphrase nên đây phải là cặp cao nhất. |
| P2 | **0.75** | | | Model đa ngữ căn hai không gian ngôn ngữ vào nhau, nhưng cặp xuyên ngữ thường thấp hơn cặp cùng ngữ một chút. |
| P3 | **0.55** | | | Cùng văn phong hành chính, cùng chứa "quy định", "học phần"/"tín chỉ" — đủ để điểm không thấp, dù chủ đề khác. |
| P4 | **0.35** | | | Đây là cặp tôi ít chắc nhất. Nếu embedding thật sự nắm ngữ nghĩa thì phải thấp; nếu nó bị từ vựng chi phối thì có thể vọt lên 0.6+. |
| P5 | **0.05** | | | Không chung miền, không chung từ. Kỳ vọng gần 0. |

**Thứ tự dự đoán (cao → thấp):** P1 > P2 > P3 > P4 > P5

## Ba điều tôi sẽ soi khi có kết quả

1. **P2 có tụt sâu dưới P1 không?** Nếu tụt nhiều thì corpus trộn `vi` + `en` là rủi ro
   thật cho benchmark: câu hỏi tiếng Việt sẽ khó kéo được điều khoản tiếng Anh của VinUni,
   và Q1–Q3 trong [`benchmark_queries.yaml`](../../data/benchmark_queries.yaml) rơi vào đúng
   tình huống đó.

2. **P4 có cao bất thường không?** Đây là phép thử "embedding có thật sự hơn tìm kiếm từ
   khóa không". P4 cao nghĩa là mô hình bị từ vựng dẫn dắt, và câu Q4 (`paraphrase`) trong
   bộ benchmark nhiều khả năng sẽ trượt.

3. **Sàn của thang điểm nằm ở đâu?** Nếu P5 ra khoảng 0.3 chứ không phải 0.05 thì cosine
   với model này **không dùng 0 làm đáy**, và mọi ngưỡng lọc kiểu "chỉ nhận score > 0.5"
   đều phải hiệu chỉnh lại theo sàn thật.
