# Bộ câu hỏi đánh giá — bảng cho REPORT_NHOM.md §3

> Nguồn máy đọc được: [`data/benchmark_queries.yaml`](../../data/benchmark_queries.yaml).
> Corpus: [`data/hoc-vu-01821/`](../../data/hoc-vu-01821) (10 tài liệu).
> Bản nháp của R4 trên corpus cá nhân — R3 chốt bộ chính thức của nhóm.

| # | Câu hỏi | Câu trả lời chuẩn (rút gọn) | Tài liệu / mục chứa thông tin |
| :-: | :-- | :-- | :-- |
| 1 | Ở VinUni, sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ chính mà không phải xin phê duyệt? | Tối đa **22 tín chỉ**. 18–22 là automatic overload (Advisor/Program Director xem xét); trên 22 cần College Dean duyệt. Phải làm đơn nếu là SV năm nhất kỳ đầu muốn >18, hoặc kỳ trước không good standing mà muốn >18. | `vinuni-academic-regulations-undergrad` — bảng *Study load variation* (Normal load / Automatic Overload / Beyond automatic overload) |
| 2 | Sinh viên VinUni được rút (withdraw) học phần muộn nhất đến khi nào, cả khóa tối đa bao nhiêu tín chỉ? | Sau khi hết hạn drop và **trước khi hoàn thành quá 30%** thời lượng học phần; nhận điểm **W**; toàn khóa tối đa **18 tín chỉ**. | `vinuni-academic-regulations-undergrad` — *Article 12. Course Add, Drop, and Withdrawal*, mục a–c của Course withdrawal policy |
| 3 | Chuyển đổi tín chỉ từ trường cũ sang VinUni được công nhận tối đa bao nhiêu, nộp hồ sơ lúc nào? | Không quá **50%** tổng tín chỉ chương trình; nộp **tuần đầu học kỳ**, xử lý trong 1 tuần sau khi hết add/drop; không nhận môn phổ thông và tín chỉ online/từ xa ngoài VinUni; đề cương phải trùng ≥80%. | `vinuni-credit-transfer` — mục *3.1 Timeline* + *3.2 Undergraduate Transfer Credit Requirements`; trần 50% nhắc lại ở `vinuni-academic-regulations-undergrad` Article 13 |
| 4 | Em đăng ký môn rồi mà chưa kịp nộp tiền học thì có bị mất môn không? | **Có** — quá thời hạn đóng học phí, Trường hủy học phần chưa đóng tiền trên hệ thống; đăng ký chỉ hoàn tất sau khi đóng học phí. | `ueh-dang-ky-huy-hoc-phan` — *Điều 4. Quy định đăng ký* |
| 5 | Sau khi bảo lưu, phải nộp đơn xin quay lại trước khi học kỳ bắt đầu bao lâu? | **Mâu thuẫn trong corpus**: Academic Regulations ghi *ít nhất 1 tuần*, Procedure ghi *ít nhất 1 tháng*. Trả lời an toàn: theo quy trình chi tiết hơn (1 tháng) và nêu rõ mâu thuẫn. | `vinuni-leave-of-absence` — bảng quy trình *Return*, bước 1 · và `vinuni-academic-regulations-undergrad` — đoạn *After returning from a temporary leave of absence* |

## Vì sao chọn 5 câu này

Năm câu cố ý **năm `kind` khác nhau**, vì đề yêu cầu câu hỏi đa dạng và vì mỗi loại làm hỏng
retrieval theo một kiểu riêng:

| Câu | kind | Cái nó thật sự đo |
| :-: | :-- | :-- |
| Q1 | `fact` | Đường cơ sở. Đáp án nằm gọn trong một bảng. **Q1 mà trượt thì lỗi không nằm ở chiến lược chunking** — nhiều khả năng store rỗng hoặc embedder đang là mock. |
| Q2 | `filtered` | Giá trị thật của `search_with_filter()`. Không lọc thì `vnuf-huong-dan-quy-che-tin-chi` (audience=faculty) là đối thủ mạnh: Điều 11 của nó dùng đúng cụm "rút bớt học phần" bằng tiếng Việt và nêu mốc 6–8 tuần — quy định của **trường khác**. Lọc `audience=student` loại nó cùng `vinuni-registrar-policy-index`. |
| Q3 | `multi_doc` | Trả lời trọn vẹn cần hai tài liệu: trần 50% có ở cả hai, nhưng mốc nộp hồ sơ chỉ có trong `vinuni-credit-transfer`. Đo được việc chunk quá lớn có nuốt mất mục *3.1 Timeline* không. |
| Q4 | `paraphrase` | Câu hỏi dùng từ đời thường ("mất môn", "nộp tiền học"), văn bản dùng từ hành chính ("hủy học phần", "đóng học phí"). Gần như không trùng từ khóa — chỗ embedding phải hơn tìm kiếm từ khóa, hoặc chỗ nó gãy. |
| Q5 | `edge` | Câu duy nhất mà một câu trả lời dứt khoát vẫn là câu trả lời **thiếu**. Retrieval tốt phải kéo cả hai tài liệu mâu thuẫn lên top-3. Agent trả lời "một tuần" hoặc "một tháng" mà không nêu mâu thuẫn thì chỉ đạt 1/2 điểm. |

Q5 là câu đáng giá nhất cho báo cáo: nó tách bạch **chất lượng truy xuất** khỏi **chất lượng
câu trả lời**. Hai chunk đúng lên top-3 mà agent vẫn trả lời sai là một kết quả có thật, và
là bằng chứng trực tiếp cho phần *Grounding Quality* trong `docs/EVALUATION.md`.

## Rủi ro đã biết của bộ câu hỏi này

Corpus gồm **5 trường khác nhau**, nên câu hỏi chung chung kiểu "sinh viên được rút học phần
khi nào" có nhiều đáp án đúng theo từng trường. Bốn trong năm câu vì vậy nêu tên trường ngay
trong câu hỏi (Q1, Q2, Q3 nói VinUni; Q4 chấm theo quy định UEH). Nếu R3 dùng corpus một
trường duy nhất thì có thể bỏ tên trường và câu hỏi sẽ tự nhiên hơn.

Q2 phụ thuộc vào việc corpus giữ tài liệu `audience` khác `student`. Nếu bộ tài liệu của
nhóm chỉ toàn `audience: student`, bộ lọc không loại đi gì và câu hỏi mất ý nghĩa —
xem [PROVENANCE](../../data/PROVENANCE-hoc-vu-01821.md).
