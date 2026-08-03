# Câu trả lời của tác tử — 5 câu hỏi đánh giá

> **PHẦN MỞ RỘNG TỰ THÊM.** Đề bài chỉ yêu cầu `KnowledgeBaseAgent.answer()`
> truy xuất → tạo prompt → gọi `llm_fn`, và cung cấp sẵn `demo_llm` (in lại
> prompt). Repo **không** cấp LLM thật và **không** nói lấy API key ở đâu.
> Nhưng `docs/SCORING.md` lại chấm 2 điểm cho "câu trả lời của tác tử chính
> xác" và `docs/EVALUATION.md` bắt xác minh câu trả lời với gold answer —
> điều không làm được với một hàm in lại prompt. Tầng trả lời dưới đây do tôi
> tự thêm để lấp khoảng trống đó, **không phải yêu cầu của đề**.

- Tầng trả lời: ExtractiveLLM (tự thêm — trích câu có sẵn, KHÔNG sinh văn bản)
- Embedder: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Corpus: `data/k3_university` — 456 chunk, chunker `recursive(chunk_size=500)`, top-k = 3

**Nó KHÔNG sinh ra chữ mới.** Nó chọn những câu có sẵn trong chunk đã truy
xuất, xếp theo độ tương tự với câu hỏi, rồi ghép kèm số nguồn. Gọi đây là
"câu trả lời do mô hình sinh ra" là mô tả sai sản phẩm.

---

## Q1 — `fact`

**Hỏi:** Ở VinUni, sinh viên đại học chính quy được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ chính mà không phải xin phê duyệt?

**Gold answer:** Tối đa 22 tín chỉ. Mức 18–22 tín chỉ là "automatic overload", do Academic Advisor hoặc Program Director xem xét. Trên 22 tín chỉ phải được College Dean (hoặc người được Dean ủy quyền) phê duyệt. Sinh viên bắt buộc làm đơn xin overload nếu thuộc một trong ba trường hợp: (i) sinh viên năm nhất học kỳ đầu muốn học hơn 18 tín chỉ; (ii) học kỳ trước không đạt good academic standing và muốn học hơn 18 tín chỉ; (iii) muốn đăng ký hơn 22 tín chỉ trong học kỳ chính.

**Bộ lọc:** `None`

**Tác tử trả lời:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Số tín chỉ sinh viên đăng ký trong học kỳ chính, học kỳ phụ phải phù hợp với quy định của Trường Đại học Kinh tế TP.Hồ Chí Minh về số tín chỉ đăng ký tối thiểu, tối đa của học kỳ cho từng hệ đào tạo; [1]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.720)
- a) 14 tín chỉ cho mỗi học kỳ, trừ học kỳ cuối khóa học, đối với những sinh viên được xếp hạng học lực bình thường; [2]  (nguồn: vnuf-huong-dan-quy-che-tin-chi, độ liên quan 0.686)
- Số tín chỉ của các học phần mà sinh viên đăng ký học vào đầu mỗi học kỳ (gọi tắt là khối lượng học tập đăng ký). [3]  (nguồn: vnuf-huong-dan-quy-che-tin-chi, độ liên quan 0.678)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (ueh-dang-ky-huy-hoc-phan, vnuf-huong-dan-quy-che-tin-chi). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q2 — `filtered`

**Hỏi:** Sinh viên VinUni được rút (withdraw) một học phần đã đăng ký muộn nhất đến khi nào, và cả khóa được rút tối đa bao nhiêu tín chỉ?

**Gold answer:** Rút học phần chỉ được thực hiện sau khi hết thời hạn drop, và phải xảy ra trước khi hoàn thành quá 30% thời lượng học của học phần đó; sau mốc này không còn được rút và sinh viên bị chấm điểm theo kết quả thực tế. Học phần đã rút nhận điểm "W" trên bảng điểm (nếu rút trước Drop Date thì không bị ghi W). Toàn bộ chương trình học chỉ được rút tối đa 18 tín chỉ; đạt giới hạn này thì không được rút nữa và phải học tiếp.

**Bộ lọc:** `{'audience': 'student'}`

**Tác tử trả lời:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Sinh viên đã có các quyết định xóa tên do bỏ học, nghỉ [1]  (nguồn: ou-quy-che-hoc-vu-tin-chi, độ liên quan 0.641)
- Sinh viên nộp “Phiếu đề nghị hủy học phần” tại P.QLĐT-CTSV theo thời gian cụ thể cho từng học kỳ trong Kế hoạch đăng ký học phần; [3]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.635)
- Quy định đối với các học phần bị hủy [2]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.598)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (ou-quy-che-hoc-vu-tin-chi, ueh-dang-ky-huy-hoc-phan). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q3 — `multi_doc`

**Hỏi:** Em muốn chuyển đổi tín chỉ đã học ở trường cũ sang VinUni thì được công nhận tối đa bao nhiêu, và phải nộp hồ sơ vào lúc nào?

**Gold answer:** Tổng số tín chỉ được chuyển đổi không vượt quá 50% tổng số tín chỉ của toàn chương trình (chiếu theo Article 13 của Academic Regulations). Hồ sơ nộp trong tuần đầu tiên của học kỳ và không muộn hơn hạn công bố trong Important Dates của kỳ nhập học đó; thường được xử lý trong vòng 1 tuần sau khi kết thúc thời gian add/drop. Hai loại không được công nhận: môn học ở bậc phổ thông (kể cả khi có bảng điểm của trường đại học cấp) và tín chỉ học online/từ xa lấy ngoài VinUni. Đề cương môn học phải trùng từ 80% nội dung trở lên so với môn tương ứng ở VinUni.

**Bộ lọc:** `None`

**Tác tử trả lời:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.643)
- VinUniversity Students, Staff and Faculty [2]  (nguồn: vinuni-leave-of-absence, độ liên quan 0.563)
- The Registrar will evaluate the request and map the external credits into specific VinUniversity courses with the support of relevant academic units. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.528)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vinuni-leave-of-absence). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q4 — `paraphrase`

**Hỏi:** Em đăng ký môn xong rồi mà chưa kịp nộp tiền học thì có bị mất môn không?

**Gold answer:** Có. Sinh viên phải đóng học phí trong thời gian quy định; sau thời hạn đó Trường sẽ hủy các học phần chưa đóng học phí của sinh viên trên hệ thống. Việc hoàn tất đăng ký chỉ được tính sau khi đã đóng học phí theo đúng thời gian của khóa/hệ tương ứng. (Quy định của Trường Đại học Kinh tế TP.HCM — UEH.)

**Bộ lọc:** `None`

**Tác tử trả lời:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- không tốt nghiệp được cấp giấy chứng nhận về các môn học đã học trong chương [3]  (nguồn: ou-quy-che-hoc-vu-tin-chi, độ liên quan 0.699)
- vắng mặt trong kỳ thi kết thúc môn học, nếu không có lý do chính đáng được [2]  (nguồn: ou-quy-che-hoc-vu-tin-chi, độ liên quan 0.677)
- Ngoài thời hạn trên học phần vẫn được giữ nguyên trong phiếu đăng ký học và nếu sinh viên không đi học sẽ được xem như tự ý bỏ học và phải nhận điểm F. [1]  (nguồn: vnuf-huong-dan-quy-che-tin-chi, độ liên quan 0.664)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (ou-quy-che-hoc-vu-tin-chi, vnuf-huong-dan-quy-che-tin-chi). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q5 — `edge`

**Hỏi:** Sau khi bảo lưu, sinh viên VinUni phải nộp đơn xin quay lại học trước khi học kỳ bắt đầu bao lâu?

**Gold answer:** Corpus có HAI mốc mâu thuẫn nhau. Academic Regulations (phần leave of absence) ghi "ít nhất một tuần trước khi học kỳ mới bắt đầu". Procedure for Requesting a Leave of Absence ghi "ít nhất một tháng trước khi bắt đầu học kỳ quay lại học". Câu trả lời an toàn là theo quy trình chi tiết hơn — nộp trước ít nhất 1 tháng — và nêu rõ có mâu thuẫn. Đơn nộp qua email của Office of Registrar hoặc nộp trực tiếp. Nếu không quay lại ngay sau khi hết thời gian bảo lưu và không xin gia hạn, hồ sơ sinh viên chuyển sang trạng thái không hoạt động và phải nộp lại hồ sơ qua Office of Admissions.

**Bộ lọc:** `None`

**Tác tử trả lời:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.766)
- After returning from a temporary leave of absence, students must complete and submit a return application to the Office of Registrar, at least one week before the start of the new semester. [3]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.663)
- Chậm nhất là một tháng sau khi sinh viên có quyết định buộc thôi học, trường phải thông báo trả về địa phương nơi sinh viên có hộ khẩu thường trú [2]  (nguồn: vnuf-huong-dan-quy-che-tin-chi, độ liên quan 0.649)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vnuf-huong-dan-quy-che-tin-chi). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```
