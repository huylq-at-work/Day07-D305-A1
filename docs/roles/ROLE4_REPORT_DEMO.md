# ROLE 4 — Integrator, Report & Demo Lead

**Người phụ trách:** *(chưa điền — vai của trưởng nhóm)* · **Branch:** `role4-report-demo`

> Đọc [docs/plan.md](../plan.md) và [docs/CONTRACTS.md](../CONTRACTS.md) trước.
> Mọi lệnh chạy từ gốc repo.

## Bạn sở hữu

- `docs/CONTRACTS.md` — định dạng đầu ra bắt buộc của cả ba role kia
- `scripts/merge_benchmark.py` — gộp 4 CSV thành `ALL.csv`
- `report/REPORT_NHOM.md` — bản ráp cuối
- `docs/plan.md`, `TEAMMATES.md` — kế hoạch và phân công
- Quyền review + merge mọi PR vào `main`

Vai này **không phải** "người ngồi cuối ráp báo cáo". Việc chính của bạn nằm ở **Giờ 1**:
chốt định dạng đầu ra trước khi ai kịp sản xuất dữ liệu. Ba người kia làm đúng theo ba định
dạng khác nhau là cách hỏng phổ biến hơn nhiều so với ai đó làm sai — và nó chỉ lộ ra ở
Giờ 4 khi không còn thời gian chạy lại.

## Bạn không được làm

- Không tự sửa nội dung mục của người khác trong `REPORT_NHOM.md`. Thấy thiếu thì **yêu cầu
  người sở hữu mục đó viết lại** — họ mới là người có số liệu và lý do.
- Không merge PR của R3 trước PR của R1. Thứ tự merge bắt buộc ở
  [TEAMMATES.md §3](../../TEAMMATES.md#thứ-tự-merge-bắt-buộc).
- Không sửa CSV kết quả của ai để bảng đẹp hơn. Số xấu vẫn là số; sửa số là gian lận và
  cũng làm phần phân tích lỗi mất nguyên liệu.
- Không quên rằng bạn **vẫn phải tự làm toàn bộ 15 TODO trong `src/`** như ba người kia.
  Vai trò quản lý không thay 30 điểm Hoàn thiện Code của cá nhân bạn.

## Nhiệm vụ

### T1 — Chốt contract (Giờ 1, trước mọi thứ khác)

Rà [docs/CONTRACTS.md](../CONTRACTS.md) với cả nhóm trong 10 phút, đặc biệt là
**Contract C** — 11 cột CSV. Ba câu phải nói rõ trong buổi rà:

- `rank_of_gold` khác `hit_top3`: rubric chấm top-1 **2 điểm** và top-3 **1 điểm**, nên chỉ
  ghi "có/không trong top-3" là vứt mất một nửa thông tin cần để chấm.
- `n_chunks_total` bắt buộc có mặt: thiếu nó thì không phân biệt được "chiến lược tốt hơn"
  với "chỉ đơn giản là chia nhiều chunk hơn".
- `params` ghi tham số **thật đã chạy**, không phải tham số dự định.

Ai không đồng ý với một cột nào thì đổi **bây giờ**. Sau Giờ 1 thì contract đóng.

### T2 — Chốt chiến lược mỗi người (Kickoff, 15 phút)

Điền bảng chiến lược ở [TEAMMATES.md §2](../../TEAMMATES.md#chiến-lược-của-từng-người-chốt-ở-kickoff).
Bốn người **bốn chiến lược khác nhau** — yêu cầu của Bài tập 3.1, không phải gợi ý. Bảo đảm
có người nhận `heading/section` (mặc định R2) vì K3 bắt buộc.

Đây là lúc chặn một sai lầm hay gặp: hai người cùng chọn `FixedSizeChunker` với tham số
hơi khác nhau. Đó không phải hai chiến lược, đó là một chiến lược chạy hai lần — và mục 2
của báo cáo sẽ không có gì để so.

### T3 — Điều phối hai lần freeze

Bạn là người theo dõi hai mốc chặn cả nhóm:

| Freeze | Ai tuyên bố | Điều kiện | Hệ quả nếu trễ |
| :-- | :-- | :-- | :-- |
| CORPUS FREEZE | R1 | ≥5 tài liệu, front matter đủ 7 khóa, `sources.csv` khớp | Ba người còn lại không chạy được gì |
| QUERY FREEZE | R3 | 5 câu đủ trường, harness chạy được | Không ai chạy benchmark được |

Corpus là **đường găng** ([plan.md §6](../plan.md#6-đường-găng-và-rủi-ro)). Hết Giờ 1 mà R1
chưa đủ 10 tài liệu: quyết định freeze với số đang có, tối thiểu 5. Quyết định này là của
bạn, và ra quyết định muộn tốn của nhóm nhiều hơn là freeze một corpus nhỏ hơn dự định.

### T4 — Review và merge PR

Đúng thứ tự: **R1 → R3 → (cả nhóm pull) → R2 → báo cáo**.

Checklist khi review:

- PR có động vào `src/` không? **`src/` không bao giờ lên `main`.** Đây là lỗi hay gặp nhất
  vì ai cũng đang sửa `src/` trên máy mình. Bắt lại ngay.
- PR có động vào file không thuộc quyền sở hữu của người đó không (bảng ở TEAMMATES §2)?
- CSV kết quả có đủ 11 cột, đúng thứ tự, có 3 dòng comment điều kiện hợp lệ ở đầu không?
- Có file `.env`, API key, `__pycache__/`, hay tài liệu chứa dữ liệu cá nhân không?

```bash
gh pr list && gh pr merge <số PR> --merge --delete-branch=false
```

### T5 — Viết `scripts/merge_benchmark.py`

```bash
python scripts\merge_benchmark.py report\benchmark\ --output report\benchmark\ALL.csv
```

Gộp 4 file × 5 dòng = 20 dòng. Script phải **báo lỗi thay vì bỏ qua** khi gặp: sai header,
thiếu cột, `strategy` ngoài enum, `query_id` không thuộc `Q1`–`Q5`, hoặc thiếu/thừa dòng
của một thành viên. Một dòng hỏng làm sai cả bốn bảng dẫn xuất cùng lúc, và sai lặng lẽ.

Kiểm tra thêm một điều mà mắt người hay bỏ sót: **`n_chunks_total` của cùng một chiến lược
phải giống nhau giữa các câu hỏi.** Khác nhau nghĩa là người đó nạp lại corpus giữa chừng —
số liệu không dùng được, phải chạy lại.

### T6 — Ráp `REPORT_NHOM.md`

Mỗi mục có đúng một người viết. Bạn ráp, kiểm tính nhất quán, và viết mục 4.

| Mục trong `REPORT_NHOM.md` | Điểm | Người viết |
| :-- | :-: | :-- |
| 1. Lựa chọn tài liệu | 10 | R1 |
| 2. Thiết kế chiến lược | 15 | R2 (tổng hợp phần của cả 4) |
| 3. Câu hỏi đánh giá & Chất lượng truy xuất | 10 | R3 |
| 4. Demo & Bài học nhóm | 5 | **R4 (bạn)** |

Ba lỗi nhất quán phải soát trước khi nộp, đều là lỗi chỉ người ráp mới thấy:

1. **Số trong văn xuôi khác số trong bảng.** Mọi con số phải truy về `ALL.csv`.
2. **Mục 2 kết luận chiến lược A thắng, mục 3 lại cho A điểm thấp nhất.** Xảy ra khi hai
   người nhìn hai lần chạy khác nhau.
3. **Mục 1 liệt kê 7 tài liệu, mục 3 dùng `gold_doc_id` của tài liệu thứ 8.** Dấu hiệu
   corpus đã đổi sau freeze.

### T7 — Demo (5 điểm)

Ba phần theo đề: chiến lược, so sánh trong nhóm, bài học. Nội dung mạnh nhất để mở đầu
không phải "nhóm em làm được X" mà là **một câu hỏi mà chiến lược A thắng còn câu khác thì
B thắng** — nó chứng minh nhóm đã thật sự so sánh chứ không chỉ chạy bốn lần.

Chuẩn bị sẵn một ca trượt để tự nêu ra. Nhóm tự chỉ ra được điểm yếu của mình gần như luôn
được đánh giá cao hơn nhóm để người khác chỉ ra.

Ghi lại phản biện từ các nhóm khác trong lúc demo — đó là nguyên liệu cho mục "Bài học" mà
bạn viết.

### T8 — Cổng cuối trước khi nộp

- [ ] Mỗi thành viên tự xác nhận `pytest tests/ -v` pass **42/42** trên máy mình
- [ ] `report/REPORT_NHOM.md` đủ 4 mục, không còn ô trống trong bảng
- [ ] Mỗi người có `report/REPORT_CANHAN_<MSSV>.md` riêng
- [ ] `ALL.csv` đủ 20 dòng, `merge_benchmark.py` chạy sạch
- [ ] Không có `.env` / API key / `__pycache__/` trong repo
- [ ] Mọi tài liệu trong `data/` có nguồn công khai, không có dữ liệu cá nhân

## Tiêu chí hoàn thành

- [ ] Contract chốt xong trong Giờ 1, cả nhóm đã đọc Contract C
- [ ] Bảng chiến lược ở TEAMMATES.md điền đủ, bốn chiến lược khác nhau
- [ ] Hai freeze diễn ra đúng thứ tự và được thông báo rõ trong nhóm
- [ ] Mọi PR merge đúng thứ tự, không PR nào lọt `src/` lên `main`
- [ ] `merge_benchmark.py` bắt được lỗi định dạng thay vì bỏ qua
- [ ] `REPORT_NHOM.md` không có mâu thuẫn số liệu giữa các mục
- [ ] Demo nêu được ít nhất một ca trượt và một ca đảo chiều thắng-thua

## Bàn giao

- Cho **cả nhóm**: contract chốt sớm, `ALL.csv` sau khi gộp, và quyết định freeze đúng lúc.
- Cho **buổi demo**: bản `REPORT_NHOM.md` cuối + một slide/khung trình bày ba phần.
- Cho **chính mình**: đừng để phần `src/` cá nhân bị bỏ lại — 30 điểm code là điểm cá nhân
  lớn nhất của bài, và nó không được cộng vào từ việc quản lý nhóm.
