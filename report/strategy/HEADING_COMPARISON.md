# So sánh baseline và HeadingChunker — Role 2

- Embedding backend đã xác nhận: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Tham số baseline: `chunk_size=200`
- Tham số HeadingChunker: `max_level=2, max_chars=1200, min_section_chars=80`

## Bảng kết quả

| Tài liệu | Chiến lược | Số chunk | Dài TB | Độ lệch | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| ou-quy-che-hoc-vu-tin-chi | fixed_size | 255 | 199.81 | 3.06 | 151 | 200 |
| ou-quy-che-hoc-vu-tin-chi | by_sentences | 79 | 479.52 | 263.63 | 134 | 1535 |
| ou-quy-che-hoc-vu-tin-chi | recursive | 228 | 164.88 | 21.49 | 81 | 198 |
| ou-quy-che-hoc-vu-tin-chi | heading | 47 | 817.53 | 362.17 | 85 | 1198 |
| vinuni-academic-regulations-undergrad | fixed_size | 459 | 199.72 | 6.06 | 70 | 200 |
| vinuni-academic-regulations-undergrad | by_sentences | 152 | 449.85 | 195.25 | 112 | 1448 |
| vinuni-academic-regulations-undergrad | recursive | 537 | 126.46 | 55.87 | 2 | 200 |
| vinuni-academic-regulations-undergrad | heading | 79 | 892.86 | 305.05 | 88 | 1198 |
| vinuni-credit-transfer | fixed_size | 34 | 199.79 | 1.18 | 193 | 200 |
| vinuni-credit-transfer | by_sentences | 9 | 568.22 | 314.87 | 173 | 1162 |
| vinuni-credit-transfer | recursive | 39 | 130.10 | 63.44 | 22 | 200 |
| vinuni-credit-transfer | heading | 5 | 1070.20 | 68.06 | 988 | 1157 |

## Ví dụ fixed-size cắt hỏng, heading giữ nguyên

Tài liệu: `ou-quy-che-hoc-vu-tin-chi`.

**Ngữ cảnh quanh ranh giới fixed-size:**

> u giáo dục đại học, quy định chuẩn kiến thức,  kỹ năng, phạm vi và cấu trúc nội dung giáo dục đại học phương pháp và hình thức  đào tạo, cách thức đánh giá kết quả đào tạo đối với mỗi môn học, ngành học,  trình độ đào tạo của giáo dục đại h

**Chunk theo heading chứa trọn ngữ cảnh:**

> Điều 2. Chương  trình giáo dục đại học  1.     Chương  trình giáo dục đại học của Trường Đại học Mở Tp. Hồ Chí Minh (sau đây gọi tắt  là chương trình) thể hiện mục tiêu giáo dục đại học, quy định chuẩn kiến thức,  kỹ năng, phạm vi và cấu trúc nội dung giáo dục đại học phương pháp và hình thức  đào tạo, cách thức đánh giá kết quả đào tạo đối với mỗi môn học, ngành học,  trình độ đào tạo của giáo dục đại học và cao đẳng.  2.     Chương  trình được xây dựng trên cơ sở chương trình khung do Bộ trưởng Bộ Giáo dục và  Đào tạo ban hành và định hướng đào tạo của Trường Đại học Mở Tp. Hồ Chí Minh.  Mỗi chương trình gắn với một ngành (kiểu đơn ngành) hoặc với một vài ngành  (kiểu song ngành; kiểu ngành chính - ngành phụ; kiểu 2 văn bằng…).  3.     Chương  trình được cấu trúc từ các môn học thuộc hai

## Nhận xét

- Fixed-size giữ độ dài đều nhưng có thể cắt giữa từ, câu hoặc điều khoản.
- Sentence chunking tránh cắt giữa câu nhưng độ dài dao động khi câu nguồn quá dài.
- Recursive chunking khống chế kích thước tốt hơn nhưng không luôn giữ tên điều khoản.
- HeadingChunker giữ tiêu đề trên từng mảnh con, giúp chunk đứng độc lập vẫn còn ngữ cảnh pháp quy.
