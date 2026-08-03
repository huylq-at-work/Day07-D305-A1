# Provenance — corpus học vụ / đăng ký học phần

> Corpus cá nhân, thu thập theo [docs/DATA_COLLECTION.md](../docs/DATA_COLLECTION.md).
> Kiểm kê máy đọc được: [`sources.csv`](k3_university/sources.csv). Danh sách URL đầu vào:
> [`../urls.csv`](urls.csv).

## Phạm vi

Lát cắt trong chủ đề cố định của K3 (dịch vụ / quy định đại học): **học vụ và đăng ký học
phần** — điều kiện đăng ký, giới hạn tín chỉ, rút/hủy học phần, bảo lưu, chuyển đổi tín chỉ.

Chọn lát cắt này vì văn bản nguồn được viết theo **điều/khoản có tiêu đề rõ ràng**, tức là
ranh giới mục mang ngữ nghĩa thật — điều kiện để so sánh chunking theo heading với chunking
theo kích thước cố định nói lên được điều gì đó.

## Bộ tài liệu

10 tài liệu, 2 ngôn ngữ, 3 nhóm `audience`.

| # | doc_id | Nguồn | Ngôn ngữ | audience | Ký tự |
| :-: | :-- | :-- | :-: | :-- | --: |
| 1 | `vinuni-academic-regulations-undergrad` | policy.vinuni.edu.vn | en | student | 68.770 |
| 2 | `vinuni-leave-of-absence` | policy.vinuni.edu.vn | en | student | 7.398 |
| 3 | `vinuni-credit-transfer` | policy.vinuni.edu.vn | en | student | 5.143 |
| 4 | `vinuni-class-schedule-registration` | registrar.vinuni.edu.vn | en | student | 3.973 |
| 5 | `vinuni-registrar-policy-index` | registrar.vinuni.edu.vn | en | **staff** | 5.476 |
| 6 | `vinuni-registrar-faqs` | registrar.vinuni.edu.vn | en | student | 4.776 |
| 7 | `ueh-dang-ky-huy-hoc-phan` | daotao.ueh.edu.vn | vi | student | 9.420 |
| 8 | `iuh-huong-dan-dang-ky-hoc-phan` | camnang.iuh.edu.vn | vi | student | 2.727 |
| 9 | `vnuf-huong-dan-quy-che-tin-chi` | vnuf.edu.vn | vi | **faculty** | 37.176 |
| 10 | `ou-quy-che-hoc-vu-tin-chi` | v1.ou.edu.vn | vi | student | 38.239 |

Corpus **cố ý** giữ hai tài liệu `audience` khác `student` (#5, #9). Không có chúng thì
`metadata_filter={"audience": "student"}` không lọc đi thứ gì, và câu hỏi cần lọc metadata
theo yêu cầu K3 sẽ không chứng minh được điều gì.

Trộn hai ngôn ngữ là chủ ý thứ hai: trường `language` trở thành một trục lọc thật, và bộ
tài liệu này kiểm được luôn khả năng đa ngữ của
`paraphrase-multilingual-MiniLM-L12-v2` — hỏi tiếng Việt có kéo được điều khoản tiếng Anh
tương ứng không.

## Ba quyết định trong lúc thu thập

**1. Đã sửa `scripts/fetch_public_pages.py` — không phải VinUni cấm crawl.**

Lần chạy đầu, cả 6 URL của VinUni bị bỏ với lý do `disallowed by robots.txt`. Kiểm tay thì
`https://policy.vinuni.edu.vn/robots.txt` trả về:

```text
User-agent: *
Disallow:
```

`Disallow:` rỗng nghĩa là **cho phép tất cả**. Nguyên nhân thật: `RobotFileParser.read()`
đọc robots.txt bằng User-Agent mặc định của urllib, WAF của site trả 403 cho UA đó, và
urllib quy ước 403 trên robots.txt = cấm toàn bộ. Kiểm chứng:

```text
UA=None                                    -> HTTP 403
UA='Day7DataFoundationsCourse/1.0 (...)'   -> HTTP 200
```

Sửa: đọc robots.txt bằng **đúng User-Agent** dùng cho trang, giữ nguyên hành vi coi 403/401
là cấm. Khai cùng một danh tính cho cả hai request cũng là cách trung thực hơn. Bản vá nằm
trong cùng commit; đáng đưa lên `main` vì nó chặn mọi nhóm dùng nguồn VinUni.

**2. Loại `ued-quy-dinh-dao-tao-dai-hoc` (ctsv.ued.udn.vn).**

Trang trả về 341 ký tự nội dung "NMF WAF - Browser Verification" — trang kiểm tra trình
duyệt, không phải văn bản quy định. Không vượt qua bằng cách giả lập trình duyệt: mục 2.3
của `DATA_COLLECTION.md` cấm né giới hạn truy cập. Đổi nguồn, còn 10 tài liệu.

**3. `document_version: not-stated` cho cả 10 tài liệu.**

Các trang policy của VinUni có tab "Policy Status" nạp bằng JavaScript nên phần crawl được
không chứa ngày hiệu lực; các trang tiếng Việt không nêu số hiệu ngay trong phần thân.
`DATA_COLLECTION.md` mục 4 cho phép `not-stated` đúng trong tình huống này. **Đây là điểm
yếu thật của corpus** — nếu cần đánh giá độ mới của quy định thì phải tra thêm bản PDF gốc,
và nên nói thẳng điều đó trong báo cáo thay vì điền một ngày phỏng đoán.

## Làm sạch

- Bỏ chrome lặp lại: "Skip to content", "Turn on more accessible mode", menu, footer bản quyền.
- Cắt phần đầu trang cho tới dòng mở đầu nội dung thật (`Điều 1`, `Chương I`, `Article`, `Purpose`).
- Gom các dải dòng trống, chuẩn hóa khoảng trắng.
- Không thêm bất kỳ câu nào không có trong nguồn (mục 2.6).

Tổng cộng cắt khoảng 13.500 ký tự chrome khỏi 10 file. Rác điều hướng đáng cắt không phải
vì tốn chỗ mà vì nó **lặp lại giống nhau giữa các trang** — chunk chứa nó có embedding gần
giống nhau và cạnh tranh trực tiếp với chunk nội dung ở top-3.

## Chạy lại

```bash
python scripts\fetch_public_pages.py data\urls.csv --output-dir data\k3_university --delay 1.5 --overwrite
```

Crawler chờ 1,5 giây giữa các request, khai `User-Agent` cố định, chỉ nhận `text/html` và
`text/plain`, và không đi theo liên kết — chỉ lấy đúng các URL trong `data/urls.csv`.
