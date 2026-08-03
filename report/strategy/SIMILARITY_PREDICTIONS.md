# Bài tập 3.3 — Dự đoán độ tương tự cosine

> **Phần dự đoán được commit TRƯỚC khi chạy** (`e8c8ee0`), kết quả điền sau — không sửa lùi
> dự đoán nào. Số liệu thô: [`similarity_results.json`](similarity_results.json).
>
> Embedder: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`EMBEDDING_PROVIDER=local`).
> Năm cặp câu lấy trong miền học vụ của corpus [`data/k3_university/`](../../data/k3_university).

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
| P1 | **0.85** | 0.8380 | −0.012 | Cùng nghĩa, cùng ngôn ngữ, cùng cấu trúc câu hỏi. Model được huấn luyện cho paraphrase nên đây phải là cặp cao nhất. |
| P2 | **0.75** | 0.7700 | +0.020 | Model đa ngữ căn hai không gian ngôn ngữ vào nhau, nhưng cặp xuyên ngữ thường thấp hơn cặp cùng ngữ một chút. |
| P3 | **0.55** | 0.5219 | −0.028 | Cùng văn phong hành chính, cùng chứa "quy định", "học phần"/"tín chỉ" — đủ để điểm không thấp, dù chủ đề khác. |
| P4 | **0.35** | **0.6028** | **+0.253** | Đây là cặp tôi ít chắc nhất. Nếu embedding thật sự nắm ngữ nghĩa thì phải thấp; nếu nó bị từ vựng chi phối thì có thể vọt lên 0.6+. |
| P5 | **0.05** | 0.0656 | +0.016 | Không chung miền, không chung từ. Kỳ vọng gần 0. |

**Thứ tự dự đoán:** P1 > P2 > P3 > P4 > P5
**Thứ tự thực tế:** P1 > P2 > **P4 > P3** > P5 — chỉ đảo đúng một cặp.

Embedder: `paraphrase-multilingual-MiniLM-L12-v2`, 384 chiều. Biên độ điểm 0.772.

## Điều gây ngạc nhiên nhất: P4

Bốn trong năm cặp lệch dưới 0.03 — gần như trúng. Cặp trượt duy nhất lệch **+0.25**, và
đó lại chính là cặp tôi dựng ra để bẫy:

> "Sinh viên **rút** học phần đã đăng ký trong học kỳ."
> "Sinh viên **rút** tiền mặt tại cây ATM trong khuôn viên trường."

Hai câu **không liên quan gì về nghĩa** — một câu về học vụ, một câu về ATM — nhưng đạt
**0.6028**, cao hơn cả P3 (0.5219) là cặp hai quy định học vụ **thật sự cùng miền** (rút
học phần vs chuyển đổi tín chỉ).

Nói cách khác: với mô hình này, "rút học phần" gần "rút tiền ATM" hơn là gần "chuyển đổi
tín chỉ". Trùng "sinh viên", "rút", "trong … trường" đủ để kéo điểm lên 0.6. Embedding
**có** nắm ngữ nghĩa — P1 và P5 chứng minh điều đó — nhưng nó không miễn nhiễm với trùng
từ vựng, đặc biệt khi câu ngắn và khung câu giống nhau.

## Ba câu hỏi đặt ra trước khi chạy, và câu trả lời

**1. Xuyên ngữ có tụt sâu không? — Không.** P2 đạt 0.7700, chỉ kém P1 (0.8380) khoảng
0.07. Corpus trộn `vi` + `en` là an toàn: câu hỏi tiếng Việt vẫn kéo được điều khoản tiếng
Anh của VinUni. Q1–Q3 trong [`benchmark_queries.yaml`](../../data/benchmark_queries.yaml)
không gặp rủi ro về ngôn ngữ.

**2. P4 có cao bất thường không? — Có, và đây là phát hiện chính.** Hệ quả trực tiếp:
ngưỡng lọc kiểu *"chỉ nhận kết quả có score > 0.5"* là **không dùng được** trên corpus này.
Ngưỡng đó vừa nhận P4 (0.60, hoàn toàn lạc đề) vừa suýt loại P3 (0.52, cùng miền). Muốn
chặn nhiễu thì phải dùng `metadata_filter`, không dùng ngưỡng điểm — đúng như thiết kế của
Q2, và giờ có số liệu đỡ lưng cho lựa chọn đó.

**3. Sàn thang điểm ở đâu? — Khoảng 0.07.** P5 ra 0.0656, tức cosine với mô hình này thật
sự dùng ~0 làm đáy. Điểm số **có** phân biệt được tín hiệu với nhiễu hoàn toàn; cái nó
không phân biệt tốt là nhiễu **trùng từ vựng**.

## Đối chứng: cùng 5 cặp chạy bằng mock embedder

| # | Nội dung | Local (thật) | Mock |
| :-: | :-- | --: | --: |
| P1 | Hai cách hỏi cùng một câu | **0.8380** | 0.0960 |
| P2 | Cùng nghĩa, vi ↔ en | 0.7700 | 0.2055 |
| P3 | Cùng miền, khác chủ đề | 0.5219 | **−0.2007** |
| P4 | Bẫy từ vựng | 0.6028 | 0.0765 |
| P5 | Học phí vs công thức nấu phở | 0.0656 | **0.1639** |

Với mock, cặp "học phí vs nấu phở" (0.164) **cao hơn** cặp hai câu hỏi cùng nghĩa (0.096),
và hai quy định cùng miền ra điểm **âm**. `_mock_embed` băm chuỗi thành vector xác định nên
nó chỉ đo trùng ký tự, không đo nghĩa.

Đây là lý do README cấm dùng mock để kết luận chiến lược nào tốt hơn — và giờ nhóm có con
số cụ thể để dẫn thay vì nhắc lại lời cảnh báo. Số liệu thô:
[`similarity_results_mock.json`](similarity_results_mock.json).

## Dự đoán rút ra cho benchmark

Q4 trong bộ câu hỏi là loại `paraphrase`: hỏi "em đăng ký môn rồi mà chưa kịp **nộp tiền
học** thì có bị **mất môn** không?" trong khi văn bản viết "**hủy học phần** chưa **đóng
học phí**". Gần như không trùng từ khóa nào.

Kết quả P1 (0.84 cho hai câu diễn đạt lại) nói rằng Q4 **có cơ hội** truy xuất đúng. Nhưng
kết quả P4 (0.60 cho hai câu lạc đề trùng từ) nói rằng các chunk khác trong corpus có chứa
"sinh viên", "học phần", "đóng học phí" sẽ **cạnh tranh rất mạnh** ở top-3. Dự đoán: Q4 lấy
được đúng tài liệu nhưng `rank_of_gold` không phải 1 — tức 1 điểm chứ không phải 2 theo
rubric. Sẽ đối chiếu khi chạy benchmark thật.
