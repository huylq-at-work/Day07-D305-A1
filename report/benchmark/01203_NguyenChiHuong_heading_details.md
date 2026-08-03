# Benchmark chi tiết — Nguyễn Chí Hướng — heading

- Backend: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Strategy: `heading(max_level=2,max_chars=1200)`
- Tổng số chunk: `218`; top-k: `3`
- Agent: `ExtractiveLLM` — chỉ trích câu có sẵn và dẫn nguồn, không sinh văn bản mới.

## Q1

**Query:** Ở VinUni, sinh viên đại học chính quy được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ chính mà không phải xin phê duyệt?

**Filter:** `{'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.6536 | `vinuni-registrar-policy-index` | Không | # Registrar Policy and Regulations Guidelines allowing eligible undergraduate students at VinUniversity to create a personalized concentration or minor by combining existing VinUni courses, subject to criteria, advisor support, and formal approval. 13. Guideline for Program Change Request Provides policies, eligibility |
| 2 | 0.6321 | `vinuni-academic-regulations-undergrad` | Không | Article 13. Transfer of Credit and Course Exemption During Registration: Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. The request should be made to the Office of Registrar.  |
| 3 | 0.5830 | `vinuni-credit-transfer` | Không | # Procedural Guidelines for Credit Transfer Requests The syllabus must cover 80% or more of the material covered in the VinUni course; use a standard textbook equivalent to that used in the VinUniversity’s course; include examinations, writing, projects, or other submitted work, produced individually or collectively, t |

**Đánh giá:** evidence rank = `99`, answer markers = `[False]`, rubric = `0/2`. Top-3 không chứa đủ bằng chứng của gold answer.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Guidelines allowing eligible undergraduate students at VinUniversity to create a personalized concentration or minor by combining existing VinUni courses, subject to criteria, advisor support, and formal approval. [1]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.675)
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [2]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.621)
- Applies to all full‑time undergraduate students receiving merit-based scholarships or financial aid at VinUni. [1]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.590)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vinuni-registrar-policy-index). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q2

**Query:** Sinh viên VinUni được rút (withdraw) một học phần đã đăng ký muộn nhất đến khi nào, và cả khóa được rút tối đa bao nhiêu tín chỉ?

**Filter:** `{'audience': 'student', 'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.6674 | `vinuni-academic-regulations-undergrad` | Không | Article 25. Grading System NGR No Grade Report This indicates that due to circumstances beyond the control of the student the Office of the Registrar did not receive the grade. The NR grade should be replaced by a letter grade as soon as possible and/or no later than graduation. W Withdrawn Assigned when a student has  |
| 2 | 0.6658 | `vinuni-academic-regulations-undergrad` | Có | Article 12. Course Add, Drop, and Withdrawal a. “W-Withdrawn” grade will be assigned on a student’s transcript when a student has registered for the course in a semester but has subsequently submitted a notification of withdrawal to the University. The “W” indicates that students attempted the class but eventually with |
| 3 | 0.6623 | `vinuni-leave-of-absence` | Không | # Procedure for Requesting a Leave of Absence Withdrawal and Return – Confirm the fulfillment of student obligations by collecting verification from various departments including the Library, Student Affairs Management, Finance Department, Financial Aid Office and IT. 05 working days since receiving the student’s reque |

**Đánh giá:** evidence rank = `2`, answer markers = `[False, False]`, rubric = `1/2`. Top-3 có bằng chứng nhưng không nằm trọn ở hạng 1, hoặc câu trả lời trích xuất còn thiếu chi tiết.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- After that date, withdrawals will no longer be permitted, and students will be graded according to their course performance. [2]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.677)
- “W-Withdrawn” grade will be assigned on a student’s transcript when a student has registered for the course in a semester but has subsequently submitted a notification of withdrawal to the University. [2]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.656)
- Assigned when a student has registered for the course in a semester but has subsequently submitted a notification of withdrawal to the University. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.635)
```

**A/B metadata filter:**

- Có filter: `['vinuni-academic-regulations-undergrad', 'vinuni-academic-regulations-undergrad', 'vinuni-leave-of-absence']`
- Không filter: `['vnuf-huong-dan-quy-che-tin-chi', 'vnuf-huong-dan-quy-che-tin-chi', 'ueh-dang-ky-huy-hoc-phan']`
- Ranking thay đổi: `True`

## Q3

**Query:** Em muốn chuyển đổi tín chỉ đã học ở trường cũ sang VinUni thì được công nhận tối đa bao nhiêu, và phải nộp hồ sơ vào lúc nào?

**Filter:** `{'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.7017 | `vinuni-academic-regulations-undergrad` | Không | Article 13. Transfer of Credit and Course Exemption During Registration: Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. The request should be made to the Office of Registrar.  |
| 2 | 0.6561 | `vinuni-registrar-policy-index` | Không | # Registrar Policy and Regulations Guidelines allowing eligible undergraduate students at VinUniversity to create a personalized concentration or minor by combining existing VinUni courses, subject to criteria, advisor support, and formal approval. 13. Guideline for Program Change Request Provides policies, eligibility |
| 3 | 0.6233 | `vinuni-credit-transfer` | Có | # Procedural Guidelines for Credit Transfer Requests The syllabus must cover 80% or more of the material covered in the VinUni course; use a standard textbook equivalent to that used in the VinUniversity’s course; include examinations, writing, projects, or other submitted work, produced individually or collectively, t |

**Đánh giá:** evidence rank = `99`, answer markers = `[False, False]`, rubric = `0/2`. Top-3 không chứa đủ bằng chứng của gold answer.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.643)
- Provides policies, eligibility criteria, timelines, and step-by-step procedures for students wishing to change their major, degree, or college at VinUniversity, with required approvals and administrative steps. [2]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.628)
- Guidelines allowing eligible undergraduate students at VinUniversity to create a personalized concentration or minor by combining existing VinUni courses, subject to criteria, advisor support, and formal approval. [2]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.596)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vinuni-registrar-policy-index). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q4

**Query:** Em đăng ký môn xong rồi mà chưa kịp nộp tiền học thì có bị mất môn không?

**Filter:** `{'institution': 'ueh'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.5074 | `ueh-dang-ky-huy-hoc-phan` | Không | Chương IV QUY ĐỊNH ĐỐI VỚI CÁC HỌC PHẦN BỊ HỦY Điều 7. Quy định đối với các học phần bị hủy Trường sẽ hủy những LHP có số lượng sinh viên đăng ký không phù hợp với quy định của Trường về điều kiện mở lớp; Nhà trường thông báo các LHP hủy trong TKB chính thức; Sinh viên đã đăng ký các LHP hủy được chuyển sang các LHP có |
| 2 | 0.5002 | `ueh-dang-ky-huy-hoc-phan` | Có | Điều 6. Đối tượng, hình thức và thời gian đăng ký Đối tượng: – Sinh viên có nhu cầu học vượt các học phần của Khóa trước; – Sinh viên có nhu cầu học và đăng ký với Hệ đào tạo khác (Áp dụng với sinh viên VB2-ĐHCQ và LT-ĐHCQ); – Sinh viên bị hủy học phần do đóng học phí không đúng hạn. Hình thức: Sinh viên nộp “Phiếu đăn |
| 3 | 0.4904 | `ueh-dang-ky-huy-hoc-phan` | Không | Điều 12. Quy định cụ thể Sinh viên phải đóng học phí ngay sau khi được Trường hỗ trợ đăng ký học phần bổ sung; Trường không giải quyết những trường hợp yêu cầu hủy học phần đăng ký bổ sung. Chươn­­g VII CÁC ĐIỀU KHOẢN KHÁC |

**Đánh giá:** evidence rank = `2`, answer markers = `[True]`, rubric = `1/2`. Top-3 có bằng chứng nhưng không nằm trọn ở hạng 1, hoặc câu trả lời trích xuất còn thiếu chi tiết.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Trường hợp không có LHP cùng thời khóa biểu, sinh viên đăng ký lại: [1]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.619)
- – Sinh viên bị hủy học phần do đóng học phí không đúng hạn. [2]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.526)
- Quy định đối với các học phần bị hủy [1]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.516)
```

## Q5

**Query:** Sau khi bảo lưu, sinh viên VinUni phải nộp đơn xin quay lại học trước khi học kỳ bắt đầu bao lâu?

**Filter:** `{'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.7349 | `vinuni-academic-regulations-undergrad` | Không | Article 13. Transfer of Credit and Course Exemption During Registration: Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. The request should be made to the Office of Registrar.  |
| 2 | 0.6310 | `vinuni-leave-of-absence` | Không | # Procedure for Requesting a Leave of Absence Withdrawal and Return – Confirm the fulfillment of student obligations by collecting verification from various departments including the Library, Student Affairs Management, Finance Department, Financial Aid Office and IT. 05 working days since receiving the student’s reque |
| 3 | 0.6143 | `vinuni-registrar-policy-index` | Không | # Registrar Policy and Regulations Policy & Regulations - Registrar Policy & Regulations Academics Policy & Regulations Policy & Regulations Policy & Regulations Request Transcripts & Certifications Class Schedule & Course Registration Transfer Credit Exams & Grades Program Change Time Away from VinUni: Leave, Withdraw |

**Đánh giá:** evidence rank = `99`, answer markers = `[False, False]`, rubric = `0/2`. Top-3 không chứa đủ bằng chứng của gold answer.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.766)
- Policies & Academic Regulations for VinUniversity students [3]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.632)
- 03 days since receiving the confirmation from the College [2]  (nguồn: vinuni-leave-of-absence, độ liên quan 0.587)

LƯU Ý: các ý trên đến từ 3 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vinuni-leave-of-absence, vinuni-registrar-policy-index). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```
