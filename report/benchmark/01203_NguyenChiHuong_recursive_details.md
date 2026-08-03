# Benchmark chi tiết — Nguyễn Chí Hướng — recursive

- Backend: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Strategy: `recursive(chunk_size=400)`
- Tổng số chunk: `598`; top-k: `3`
- Agent: `ExtractiveLLM` — chỉ trích câu có sẵn và dẫn nguồn, không sinh văn bản mới.

## Q1

**Query:** Ở VinUni, sinh viên đại học chính quy được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ chính mà không phải xin phê duyệt?

**Filter:** `{'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.6469 | `vinuni-academic-regulations-undergrad` | Không | Grades shall not be posted publicly in any way that may be associated with specific students. However, anonymized statistics may be posted for internal use at VinUniversity. Each College sets its criteria for affiliation to a major, based on minimum grades in certain courses and/or overall grade-point-average. |
| 2 | 0.6369 | `vinuni-registrar-policy-index` | Không | Guidelines allowing eligible undergraduate students at VinUniversity to create a personalized concentration or minor by combining existing VinUni courses, subject to criteria, advisor support, and formal approval. 13. Guideline for Program Change Request |
| 3 | 0.6332 | `vinuni-academic-regulations-undergrad` | Không | During Registration: Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. The request should be made to the Office of Registrar. |

**Đánh giá:** evidence rank = `99`, answer markers = `[False]`, rubric = `0/2`. Top-3 không chứa đủ bằng chứng của gold answer.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Guidelines allowing eligible undergraduate students at VinUniversity to create a personalized concentration or minor by combining existing VinUni courses, subject to criteria, advisor support, and formal approval. [2]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.675)
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [3]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.621)
- Each College sets its criteria for affiliation to a major, based on minimum grades in certain courses and/or overall grade-point-average. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.578)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vinuni-registrar-policy-index). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q2

**Query:** Sinh viên VinUni được rút (withdraw) một học phần đã đăng ký muộn nhất đến khi nào, và cả khóa được rút tối đa bao nhiêu tín chỉ?

**Filter:** `{'audience': 'student', 'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.6724 | `vinuni-academic-regulations-undergrad` | Có | b. Withdrawal from a course is permitted after the course dropping period and must occur before completing no more than 30% of the study time for that course. After that date, withdrawals will no longer be permitted, and students will be graded according to their course performance. If the student withdraws before the  |
| 2 | 0.6674 | `vinuni-academic-regulations-undergrad` | Không | W Withdrawn Assigned when a student has registered for the course in a semester but has subsequently submitted a notification of withdrawal to the University. If the student withdraws before the “Drop Date” for each semester, no W grade should be recorded on the transcript. Minimum credit threshold decisions have to be |
| 3 | 0.6596 | `vinuni-academic-regulations-undergrad` | Có | c. The withdrawal limit policy allows students to withdraw from a maximum of 18 credits over the entire program of study. Once the limit is reached, students can no longer withdraw and must remain enrolled. The instructor(s) will assign appropriate grades(s). Article 13. Transfer of Credit and Course Exemption Transfer |

**Đánh giá:** evidence rank = `3`, answer markers = `[False, True]`, rubric = `1/2`. Top-3 có bằng chứng nhưng không nằm trọn ở hạng 1, hoặc câu trả lời trích xuất còn thiếu chi tiết.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- After that date, withdrawals will no longer be permitted, and students will be graded according to their course performance. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.677)
- Assigned when a student has registered for the course in a semester but has subsequently submitted a notification of withdrawal to the University. [2]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.635)
- The withdrawal limit policy allows students to withdraw from a maximum of 18 credits over the entire program of study. [3]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.595)
```

**A/B metadata filter:**

- Có filter: `['vinuni-academic-regulations-undergrad', 'vinuni-academic-regulations-undergrad', 'vinuni-academic-regulations-undergrad']`
- Không filter: `['vnuf-huong-dan-quy-che-tin-chi', 'ueh-dang-ky-huy-hoc-phan', 'ou-quy-che-hoc-vu-tin-chi']`
- Ranking thay đổi: `True`

## Q3

**Query:** Em muốn chuyển đổi tín chỉ đã học ở trường cũ sang VinUni thì được công nhận tối đa bao nhiêu, và phải nộp hồ sơ vào lúc nào?

**Filter:** `{'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.7014 | `vinuni-academic-regulations-undergrad` | Không | During Registration: Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. The request should be made to the Office of Registrar. |
| 2 | 0.6376 | `vinuni-academic-regulations-undergrad` | Không | Educational Affairs Committee Issuing Date: Oct 30, 2024 Applying for: All VinUniversity Security Classification: Public Related Documents and Forms: Procedural Guidelines for Credit Transfer Requests Record of Changes Revision Date Author / Editor Description V1.0 May 22, 2020 Prepared by: Head of Registrar Reviewed b |
| 3 | 0.6358 | `vinuni-registrar-policy-index` | Không | Provides policies, eligibility criteria, timelines, and step-by-step procedures for students wishing to change their major, degree, or college at VinUniversity, with required approvals and administrative steps. 14. Student Grade Appeal Procedure Transparent and equitable process for appealing a final course grade. |

**Đánh giá:** evidence rank = `99`, answer markers = `[False, False]`, rubric = `0/2`. Top-3 không chứa đủ bằng chứng của gold answer.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.643)
- Provides policies, eligibility criteria, timelines, and step-by-step procedures for students wishing to change their major, degree, or college at VinUniversity, with required approvals and administrative steps. [3]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.628)
- Student Grade Appeal Procedure [3]  (nguồn: vinuni-registrar-policy-index, độ liên quan 0.455)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vinuni-registrar-policy-index). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```

## Q4

**Query:** Em đăng ký môn xong rồi mà chưa kịp nộp tiền học thì có bị mất môn không?

**Filter:** `{'institution': 'ueh'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.6225 | `ueh-dang-ky-huy-hoc-phan` | Không | Sinh viên phải học theo thời khóa biểu đã đăng ký (đóng học phí) và không được điều chỉnh. Trường không giải quyết trường hợp học nhầm lớp học phần, thi nhầm lớp học phần, tự chuyển lớp học phần; |
| 2 | 0.5781 | `ueh-dang-ky-huy-hoc-phan` | Không | Sinh viên không đăng ký học phần 2 học kỳ liên tiếp phải làm “Đơn xin nghỉ học tạm thời và bảo lưu kết quả học tập”. Sinh viên không nộp đơn sẽ bị xử lý học vụ đăng ký học phần, bị buộc thôi học (xử lý học vụ đăng ký học phần theo quy chế đăng ký học vụ của Trường). Điều 14. Hiệu lực và trách nhiệm thi hành |
| 3 | 0.5408 | `ueh-dang-ky-huy-hoc-phan` | Không | Sinh viên không được đăng ký các học phần có điểm X (học phần chưa nhận điểm thi); Trường hợp sinh viên không đăng ký được vì LHP đã hết khả năng tiếp nhận, sinh viên phải đợi đăng ký vào các học kỳ sau. Điều 5. Quy trình đăng ký P.QLĐT-CTSV đăng ký trong tài khoản cho sinh viên TKB dự kiến; |

**Đánh giá:** evidence rank = `99`, answer markers = `[False]`, rubric = `0/2`. Top-3 không chứa đủ bằng chứng của gold answer.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Sinh viên không đăng ký học phần 2 học kỳ liên tiếp phải làm “Đơn xin nghỉ học tạm thời và bảo lưu kết quả học tập”. [2]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.634)
- Sinh viên phải học theo thời khóa biểu đã đăng ký (đóng học phí) và không được điều chỉnh. [1]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.621)
- Sinh viên không được đăng ký các học phần có điểm X (học phần chưa nhận điểm thi); [3]  (nguồn: ueh-dang-ky-huy-hoc-phan, độ liên quan 0.604)
```

## Q5

**Query:** Sau khi bảo lưu, sinh viên VinUni phải nộp đơn xin quay lại học trước khi học kỳ bắt đầu bao lâu?

**Filter:** `{'institution': 'vinuni'}`

| Hạng | Score | doc_id | Có marker đáp án? | Preview |
|---:|---:|---|:---:|---|
| 1 | 0.7633 | `vinuni-academic-regulations-undergrad` | Không | During Registration: Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. The request should be made to the Office of Registrar. |
| 2 | 0.6644 | `vinuni-class-schedule-registration` | Không | Time Away from VinUni: Leave, Withdraw, Return Graduation Forms & Petitions Class Schedule & Course Registration Welcome to the course registration hub. This page guides you through how to prepare, register, and manage your courses at VinUni. Class Schedule |
| 3 | 0.6420 | `vinuni-academic-regulations-undergrad` | Có | After returning from a temporary leave of absence, students must complete and submit a return application to the Office of Registrar, at least one week before the start of the new semester. The form must be accompanied by documentation that explains their progress during the leave that would enable them to return succe |

**Đánh giá:** evidence rank = `99`, answer markers = `[False, True]`, rubric = `0/2`. Top-3 không chứa đủ bằng chứng của gold answer.

**Câu trả lời của agent:**

```text
[trích xuất từ ngữ cảnh, không phải văn bản do mô hình sinh]
- Current students who complete studies elsewhere during their registration at VinUniversity must submit applications no later than one month after a student’s return to study at VinUniversity. [1]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.766)
- After returning from a temporary leave of absence, students must complete and submit a return application to the Office of Registrar, at least one week before the start of the new semester. [3]  (nguồn: vinuni-academic-regulations-undergrad, độ liên quan 0.663)
- Class Schedule & Course Registration [2]  (nguồn: vinuni-class-schedule-registration, độ liên quan 0.472)

LƯU Ý: các ý trên đến từ 2 tài liệu khác nhau (vinuni-academic-regulations-undergrad, vinuni-class-schedule-registration). Kiểm tra xem chúng có cùng áp dụng cho trường hợp của bạn không trước khi dùng.
```
