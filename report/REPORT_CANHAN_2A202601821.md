# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Quang Huy — **MSSV:** 2A202601821
**Nhóm:** K3 — D305-A1 · **Vai:** Integrator, Report & Demo Lead
**Ngày:** 2026-08-03 · **Nhánh:** `01821-LeQuangHuy`

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

Embedding biến mỗi câu thành một mũi tên trong không gian 384 chiều. Cosine đo **góc** giữa
hai mũi tên, không quan tâm chúng dài ngắn ra sao. Điểm gần 1 nghĩa là hai mũi tên gần như
cùng hướng — mô hình "hiểu" hai đoạn văn nói về cùng một chuyện, dù dùng từ khác nhau.

**Ví dụ có độ tương tự CAO:** *(số đo thật, không phải phỏng đoán — xem Phần 4)*
- Câu A: "Sinh viên được rút học phần đã đăng ký muộn nhất khi nào?"
- Câu B: "Hạn chót để sinh viên hủy một môn đã đăng ký là bao giờ?"
- Điểm đo được: **0.8380**
- Tại sao tương đồng: cùng hỏi một chuyện, dù không dùng chung động từ ("rút" vs "hủy") lẫn
  cách diễn đạt thời hạn ("muộn nhất" vs "hạn chót"). Đây đúng là thứ tìm kiếm từ khóa bỏ sót.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Hạn nộp học phí học kỳ 1 là ngày nào?"
- Câu B: "Công thức nấu phở bò truyền thống của Hà Nội."
- Điểm đo được: **0.0656**
- Tại sao khác: không chung miền, không chung từ vựng. Con số này cũng cho biết **sàn** thực
  tế của thang điểm là ~0.07 chứ không phải 0 tuyệt đối.

**Tại sao cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**

Vì cosine **chia cho độ dài vector**, nên nó chỉ đo hướng. Một câu hỏi 10 từ và một điều
khoản 500 ký tự cùng nội dung sẽ có vector cùng hướng nhưng độ lớn khác nhau; với Euclid thì
đoạn dài luôn "xa" câu ngắn chỉ vì nó dài hơn, còn cosine coi chúng là giống nhau. Trong
retrieval ta so **câu hỏi ngắn** với **chunk dài** ở mọi truy vấn, nên đặc tính đó là bắt buộc.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunk?**

```
số chunk = ceil((10000 - 50) / (500 - 50))
         = ceil(9950 / 450)
         = ceil(22.11)
         = 23 chunk
```

**Đáp án: 23 chunk.** Mỗi bước nhảy 450 ký tự (bước trượt = `chunk_size − overlap`), riêng
chunk đầu tiên phủ trọn 500.

**Nếu overlap tăng lên 100 thì sao?**

```
ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunk
```

Tăng 2 chunk (23 → 25). Overlap lớn hơn thì bước trượt ngắn lại nên cần nhiều chunk hơn để
phủ hết tài liệu — tốn thêm chỗ lưu và thêm vector phải so mỗi lần tìm.

Đổi lại: overlap tồn tại để **cứu câu bị cắt ngang ranh giới**. Cắt cứng theo kích thước
không quan tâm ngữ nghĩa, nên một điều khoản có thể bị xẻ đôi giữa hai chunk và không chunk
nào trả lời được. Overlap khiến phần giáp ranh xuất hiện trọn vẹn trong ít nhất một chunk.

Thực nghiệm ở Phần 5 cho thấy vấn đề này sâu hơn công thức: tôi chuyển hẳn sang
`RecursiveChunker` — cắt theo `\n\n` → `\n` → `. ` → `" "` — để **cắt ở chỗ ít gây tổn hại
nhất** ngay từ đầu, thay vì cắt bừa rồi dùng overlap vá lại.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

Dùng `re.split(r"(?<=[.!?])\s+", text)`. Lookbehind giữ lại dấu câu ở cuối mỗi câu thay vì
nuốt mất nó, còn `\s+` gộp luôn cả `". "` lẫn `".\n"` thành một quy tắc. Ca ngoại lệ đã xử
lý: chuỗi rỗng hoặc toàn khoảng trắng trả `[]`, câu rỗng sau khi `strip()` bị loại nên không
sinh chunk trống.

Điều đáng nói hơn là **giới hạn** của chiến lược này, đo được ở Phần 5: nó gom đúng N câu
bất kể dài ngắn, nên **không hề tôn trọng `chunk_size`**. Trên `vinuni-academic-regulations`
nó đẻ ra chunk **1868 ký tự** nằm cạnh chunk 156 ký tự, độ lệch chuẩn 205.6 — gấp 20 lần
`FixedSizeChunker`. Với văn bản quy định, một "câu" có thể là cả một khoản liệt kê dài.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

Thử lần lượt 5 dấu phân cách theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Ý tưởng
là **cắt ở chỗ ít gây tổn hại nhất**: ranh giới đoạn văn giữ trọn ý, cắt giữa từ là tệ nhất.

Ba base case: đoạn ngắn hơn `chunk_size` → trả nguyên; hết dấu phân cách hoặc gặp `""` →
cắt cứng; dấu hiện tại không có trong đoạn → **đệ quy xuống dấu kế tiếp** thay vì cắt bừa.
Sau khi tách, tôi gộp các mảnh liền nhau cho tới sát `chunk_size` rồi mới đệ quy phần còn
quá dài — nếu không sẽ ra hàng loạt mẩu vụn một dòng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

Nhúng **đúng một lần** lúc nạp, lưu vector ngay trong bản ghi. Mỗi lần `search()` chỉ nhúng
**câu hỏi** rồi so với 456 vector có sẵn — nếu nhúng lại toàn bộ chunk mỗi lần tìm thì một
truy vấn phải chạy mô hình 456 lần cho ra kết quả y hệt. Đây chính là lý do vector store tồn
tại: trả tiền tính toán một lần lúc nạp, tìm kiếm về sau thì rẻ.

Xếp hạng bằng `compute_similarity` (cosine). Tôi có kiểm và thấy cả `MockEmbedder` lẫn
`LocalEmbedder` đều trả vector **đã chuẩn hoá L2**, nên tích vô hướng bằng đúng cosine —
dùng cosine vẫn an toàn hơn nếu sau này thay embedder không chuẩn hoá.

Một chi tiết nhỏ mà không test nào bắt được: `_make_record` **copy** metadata
(`dict(doc.metadata or {})`). Không copy thì store dùng chung dict với `Document` bên ngoài;
ai sửa metadata sau khi nạp sẽ âm thầm đổi dữ liệu trong store và bộ lọc bắt đầu cho kết quả
khác mà không ai hiểu vì sao.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

**Lọc trước, xếp hạng sau.** Đây là chỗ dễ viết sai nhất mà vẫn pass test: nếu xếp hạng
trước rồi lọc sau thì bộ lọc chỉ tỉa phần đuôi của top-k, và chunk đúng nằm ở hạng 5 sẽ
không bao giờ có cơ hội xuất hiện. Lọc trước thì nó được xét trong tập nhỏ hơn và nổi lên.

`delete_document` khớp theo **ba cách**: `metadata["doc_id"]` (đường đi qua
`ingest.build_knowledge_base`), `id` trùng nguyên (Document nạp trực tiếp), và tiền tố
`"<doc>::"` (quy ước của `ingest.chunk_document`). Chỉ so `record["id"]` là đủ pass test —
test tạo `Document` có `id` trùng luôn `doc_id` — nhưng trên corpus thật, id là
`"vinuni-credit-transfer::chunk_0"` nên sẽ xoá **0 chunk** và trả `False`. Loại lỗi chỉ hiện
khi chạy dữ liệu thật, không hiện trong `pytest`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

Truy xuất bằng `search_with_filter()` (bao luôn `search()` khi không có bộ lọc), rồi ghép
ngữ cảnh dưới dạng khối đánh số `[1] [2] [3]`, mỗi khối kèm `doc_id` và `score`. Đánh số là
để câu trả lời truy ngược được về đúng chunk nào — không có nó thì không chấm được tiêu chí
*Grounding Quality*. Prompt đặt bốn ràng buộc: chỉ dùng ngữ cảnh, dẫn số nguồn cho từng ý,
nêu rõ khi các nguồn mâu thuẫn, và nói "không đủ thông tin" thay vì suy đoán. Khi truy xuất
trả về rỗng thì `answer()` trả câu "không tìm thấy thông tin liên quan" mà **không gọi
`llm_fn`** — trả lời "không biết" đúng lúc là hành vi đúng của RAG, không phải thất bại.

#### Phần mở rộng tự thêm — `scripts/extractive_llm.py`

> **KHÔNG PHẢI YÊU CẦU CỦA ĐỀ.** `exercises.md` chỉ yêu cầu `answer()` truy xuất → tạo
> prompt → gọi `llm_fn`, và `main.py` cung cấp sẵn `demo_llm` (in lại prompt). Toàn bộ
> phần dưới đây là do tôi tự thêm, nằm ngoài `src/`, và có thể bỏ đi mà không ảnh hưởng
> tới 42/42 test.

Lý do thêm: `docs/SCORING.md` chấm 2 điểm cho *"câu trả lời của tác tử chính xác"* và
`docs/EVALUATION.md` bắt xác minh câu trả lời với gold answer — nhưng repo không cấp LLM
thật, cũng không nói lấy API key ở đâu. Với `demo_llm` in lại prompt thì **không xác minh
được gì**. Đây là khoảng trống trong bộ tài liệu của đề, và tôi lấp bằng một tầng trả lời
chạy offline.

`ExtractiveLLM` **không sinh ra chữ mới**: nó tách các câu có sẵn trong chunk đã truy xuất,
chấm từng câu bằng chính `compute_similarity()`, lấy tối đa 3 câu vượt ngưỡng 0.35, rồi ghép
kèm `[n]`. Dưới ngưỡng thì trả về "ngữ cảnh không đủ liên quan" kèm điểm cao nhất đo được.
Ngưỡng 0.35 lấy từ số đo ở Phần 4: cặp câu hoàn toàn không liên quan cho ~0.07, cặp cùng
miền cho ~0.52.

Gọi đây là "câu trả lời do mô hình sinh ra" là mô tả sai sản phẩm. Nó không diễn giải, không
tổng hợp hai nguồn thành một câu, không trả lời được câu hỏi cần suy luận.

**Kết quả chạy trên 5 câu hỏi** ([`report/benchmark/ANSWERS.md`](benchmark/ANSWERS.md)): câu
trả lời **sai ở hầu hết các câu** — nhưng sai vì tầng truy xuất đã hỏng (0/10), không phải
vì tầng trả lời. Đây chính là điều đáng nói: chất lượng câu trả lời là **hệ quả** của chất
lượng truy xuất, không cứu được bằng prompt.

Ca đáng chú ý nhất là Q5. Tác tử trả lời bằng câu *"must submit applications no later than
one month after a student's return to study at VinUniversity"* — nghe khớp hoàn hảo với câu
hỏi "nộp đơn quay lại trước bao lâu", có cả "one month" lẫn "return to study". Nhưng câu đó
nói về **hạn nộp hồ sơ chuyển đổi tín chỉ**, không phải quy trình quay lại sau bảo lưu. Một
câu trả lời trông đúng, dẫn nguồn đầy đủ, truy ngược được về chunk thật — mà vẫn sai. Đó là
kiểu lỗi nguy hiểm nhất của RAG, và là lý do tiêu chí *Factual Accuracy* tồn tại tách khỏi
*Retrieval Precision*.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
$ pytest tests/ -q --tb=no
..........................................                               [100%]
42 passed in 0.06s
```

Đường đi từ đầu tới cuối, chụp lại được trong repo:

| Mốc | Kết quả | Bằng chứng |
| :-- | :-- | :-- |
| Trước khi làm gì | **11 / 42** | [`report/baseline/pytest_v0.txt`](baseline/pytest_v0.txt) |
| Sau khi xong `chunking.py` | 26 / 42 | commit `e8c8ee0` |
| Sau khi xong `store.py` + `agent.py` | **42 / 42** | commit `9df5e23` |

11 test pass sẵn từ đầu không phải may — chúng chấm phần đề đã cho (`Document`,
`FixedSizeChunker`, cấu trúc package). 31 test còn lại là phần phải tự kiếm.

Thứ tự tôi làm không theo thứ tự file mà theo **cái gì mở khoá được nhiều nhất**:
`compute_similarity` (4 test, và `_search_records` dùng lại nó) → hai chunker (8 test) →
`EmbeddingStore` (14 test, và là thứ `run_benchmark.py` gọi tới) → `compare()` (3 test, cần
cả ba chunker xong) → `KnowledgeBaseAgent` (2 test).

**Số lượng bài test vượt qua (pass): 42 / 42**

> Kiểm chéo: 42/42 chạy trên Python 3.14.6. Chuẩn của lab là 3.11 (`.python-version`) —
> đây là điểm lệch môi trường tôi chưa khắc phục được vì máy chỉ cài sẵn 3.14.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Dự đoán được commit **trước** khi chạy (`e8c8ee0`), kết quả điền sau — không sửa lùi dự
> đoán nào. Chi tiết: [`report/strategy/SIMILARITY_PREDICTIONS.md`](strategy/SIMILARITY_PREDICTIONS.md),
> số liệu thô: [`similarity_results.json`](strategy/similarity_results.json).

| Cặp | Câu A | Câu B | Dự đoán | Thực tế | Đúng? |
|:-:|---|---|--:|--:|:-:|
| 1 | "Sinh viên được rút học phần đã đăng ký muộn nhất khi nào?" | "Hạn chót để sinh viên hủy một môn đã đăng ký là bao giờ?" | 0.85 (cao) | **0.8380** | ✅ lệch 0.012 |
| 2 | "Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ?" | "What is the maximum number of credits a student may register in one semester?" | 0.75 (cao) | **0.7700** | ✅ lệch 0.020 |
| 3 | "Quy định về rút học phần đã đăng ký." | "Quy định về chuyển đổi tín chỉ từ trường khác." | 0.55 (vừa) | **0.5219** | ✅ lệch 0.028 |
| 4 | "Sinh viên **rút** học phần đã đăng ký trong học kỳ." | "Sinh viên **rút** tiền mặt tại cây ATM trong khuôn viên trường." | 0.35 (thấp) | **0.6028** | ❌ lệch **0.253** |
| 5 | "Hạn nộp học phí học kỳ 1 là ngày nào?" | "Công thức nấu phở bò truyền thống của Hà Nội." | 0.05 (thấp) | **0.0656** | ✅ lệch 0.016 |

Thứ tự dự đoán `P1 > P2 > P3 > P4 > P5`; thực tế `P1 > P2 > **P4 > P3** > P5` — đảo đúng một cặp.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Bốn cặp lệch dưới 0.03. Cặp trượt duy nhất — P4 — lại chính là cặp tôi dựng ra để bẫy, và nó
lệch **+0.25**.

Hai câu "rút học phần" và "rút tiền ATM" **không liên quan gì về nghĩa**, nhưng đạt 0.6028 —
**cao hơn** P3 (0.5219) là cặp hai quy định học vụ *thật sự cùng miền*. Nói cách khác: với mô
hình này, "rút học phần" gần "rút tiền ATM" hơn là gần "chuyển đổi tín chỉ". Trùng "sinh
viên", "rút", "trong… trường" là đủ để kéo điểm lên 0.6.

Embedding **có** nắm ngữ nghĩa — P1 (0.84) và P5 (0.07) chứng minh điều đó rõ ràng. Nhưng nó
không miễn nhiễm với **trùng từ vựng**, nhất là khi câu ngắn và khung câu giống nhau.

Hệ quả thực dụng, và đây là thứ tôi mang sang thiết kế hệ thống: **ngưỡng lọc theo điểm là
không dùng được**. Quy tắc kiểu *"chỉ nhận kết quả score > 0.5"* vừa nhận P4 (0.60, hoàn toàn
lạc đề) vừa suýt loại P3 (0.52, đúng miền). Muốn chặn nhiễu thì phải lọc bằng **metadata**,
không lọc bằng điểm — và Phần 5 cho thấy đúng như vậy.

**Đối chứng: cùng 5 cặp chạy bằng mock embedder**

| Cặp | Local (thật) | Mock |
|:-:|--:|--:|
| 1 — hai cách hỏi cùng một câu | **0.8380** | 0.0960 |
| 3 — cùng miền, khác chủ đề | 0.5219 | **−0.2007** |
| 5 — học phí vs công thức nấu phở | 0.0656 | **0.1639** |

Với mock, "học phí vs nấu phở" (0.164) **cao hơn** hai câu hỏi cùng nghĩa (0.096), và hai quy
định cùng miền ra điểm **âm**. `_mock_embed` băm chuỗi thành vector xác định nên nó chỉ đo
trùng ký tự, không đo nghĩa. Đây là lý do README cấm dùng mock để kết luận chiến lược nào tốt
hơn — và giờ có con số cụ thể để dẫn thay vì nhắc lại lời cảnh báo.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Chiến lược của tôi: **`RecursiveChunker`, `chunk_size=500`** (chốt sau khi quét 300/500/800 —
xem [`CHUNK_SIZE_SWEEP.md`](strategy/CHUNK_SIZE_SWEEP.md)). Corpus 10 tài liệu → **456 chunk**,
embedder `paraphrase-multilingual-MiniLM-L12-v2`. Số liệu:
[`01821-LeQuangHuy_recursive.csv`](benchmark/01821-LeQuangHuy_recursive.csv).

| # | Câu hỏi | Top-1 chunk truy xuất được | Score | Liên quan? | Agent trả lời |
|:-:|---|---|--:|:-:|---|
| Q1 | Tối đa bao nhiêu tín chỉ/kỳ không cần phê duyệt? | `vinuni-academic-regulations` — bảng study load | 0.6469 | ✅ hạng 1 | Sai — top-3 không chứa đoạn "18-22 credits" |
| Q2 | Rút học phần muộn nhất khi nào, tối đa bao nhiêu tín chỉ? | `vinuni-academic-regulations` — Article 12 | 0.6743 | ✅ hạng 1 | Đúng ý chính (30% thời lượng, điểm W) |
| Q3 | Chuyển đổi tín chỉ tối đa bao nhiêu, nộp khi nào? | `vinuni-academic-regulations` — Article 13 | 0.7126 | ⚠️ gold hạng 6 | Thiếu mốc thời gian nộp hồ sơ |
| Q4 | Chưa nộp tiền học thì có mất môn không? | `ueh-dang-ky-huy-hoc-phan` | 0.6064 | ✅ hạng 1 | Sai — lấy nhầm câu về điểm X |
| Q5 | Sau bảo lưu nộp đơn quay lại trước bao lâu? | `vinuni-academic-regulations` | 0.7637 | ⚠️ gold hạng 5 | **Sai mà trông đúng** — xem dưới |

**Bao nhiêu câu trả về chunk liên quan trong top-3? 3 / 5** — điểm truy xuất **6/10**.

### Ba điều đo được, quan trọng hơn con số 6/10

**1. Metadata cứu được bài, điểm số thì không.** Vòng chạy đầu tôi được **0/10**. Cả 5 câu
đều bị chunk của **trường khác** chiếm top-1: hỏi về VinUni nhưng nhận về quy định của ĐH
Lâm nghiệp, ĐH Mở, UEH — vì embedding không đánh trọng số cho tên trường, nó chỉ thấy "sinh
viên", "tín chỉ", "học kỳ". Thêm trường `institution` vào metadata rồi lọc theo nó, **không
đổi gì khác**: 0/10 → 6/10, Q1 từ hạng 7 lên 1, Q2 từ 5 lên 1.

Đây đúng là hệ quả của phát hiện ở Phần 4: thứ embedding không phân biệt được thì metadata
phân biệt được.

**2. Hai trong sáu điểm đó không đáng tin, và tôi phải nói ra.** Q4 lọc `institution=ueh`, mà
UEH chỉ có **một tài liệu** (23 chunk). `rank_of_gold` đo ở mức tài liệu, nên pool còn một
tài liệu thì hạng 1 gần như được cho không. Điểm thật đáng tin là **Q1 + Q2 = 4/10** — cả hai
lọc `vinuni` với pool 250 chunk / 6 tài liệu, vẫn là bài toán thật.

**3. `rank_doc = 1` không có nghĩa agent đọc được câu trả lời.** Q1 được 2 điểm rubric, nhưng
đoạn thật sự chứa "18-22 credits" nằm ở **hạng 71**. Tài liệu lên hạng 1 nhờ một chunk khác.
Rubric chấm ở mức **tài liệu**, agent đọc ở mức **chunk** — hai mức đó lệch nhau và điểm số
che mất khoảng lệch.

Q5 là ca nguy hiểm nhất. Agent trả lời *"must submit applications no later than **one month**
after a student's **return to study**"* — có dẫn nguồn, truy ngược được về chunk thật, đọc
lên khớp hoàn hảo với câu hỏi. Nhưng câu đó nói về **hạn nộp hồ sơ chuyển đổi tín chỉ**, không
phải quy trình quay lại sau bảo lưu. Câu trả lời trông đúng, có trích dẫn đầy đủ, mà vẫn sai.
Đó là lý do `docs/EVALUATION.md` tách *Factual Accuracy* khỏi *Retrieval Precision*.

**Điều hay nhất tôi học được từ thành viên khác:**

`HeadingChunker` của **Nguyễn Chí Hướng**. Chạy trên đúng corpus và đúng 5 câu hỏi của tôi:
**5/5 lọt top-3, 8/10** — hơn hẳn `RecursiveChunker` của tôi (3/5, 6/10). Hai câu tôi luôn
trượt (Q3, Q5) đều được nó kéo lên hạng 2.

Không phải vì chunk to nhỏ khác nhau: `recursive` 800 và `heading` 800 gần bằng nhau (684 vs
599 ký tự) nhưng chênh 2 điểm. Khác biệt ở **chỗ đặt nhát cắt** — tôi cắt theo `\n\n`/`\n`
tức theo hình thức trình bày, bạn ấy cắt theo `Điều`/`Chương`/`Article` tức theo ranh giới do
người soạn văn bản đặt ra. Cộng thêm chi tiết tôi không nghĩ ra: khi mục dài quá hạn, bạn ấy
**đính lại tiêu đề vào từng mảnh con**, nên chunk đứng một mình vẫn biết nó thuộc Điều nào.

Kết quả này còn **bác bỏ một kết luận của chính tôi**. Tôi từng đo được mô hình chỉ nhận 128
token và khuyên giữ chunk dưới ~550 ký tự để không bị cắt cụt. Nhưng cấu hình tốt nhất của
bạn Hướng có **66% số chunk vượt trần**. Lý do: cắt cụt cắt phần **đuôi**, mà tiêu đề nằm ở
**đầu** nên phần định danh quan trọng nhất luôn sống sót. Lời khuyên của tôi đúng với chunker
của tôi, không đúng với chunker biết đặt tiêu đề lên trước.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá | Căn cứ |
|----------|:-:|:--|
| Khởi động (Warm-up) | 5 / 5 | Giải thích cosine kèm số đo thật; bài toán chunking có phép tính đầy đủ cho cả hai mức overlap |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 | Nêu được cả lựa chọn lẫn **lý do**, kèm ca hỏng mà test không bắt được. Trừ 1: chưa quét bộ separator |
| Hoàn thiện code (tests) | 30 / 30 | 42 / 42, có mốc 11 → 26 → 42 truy được trong git |
| Dự đoán độ tương tự | 5 / 5 | Dự đoán commit trước khi chạy; 4/5 lệch < 0.03; cặp trượt được phân tích thành kết luận dùng được |
| Kết quả truy xuất của tôi | 7 / 10 | 3/5 top-3, 6/10 điểm truy xuất. Tự trừ vì Q3/Q5 vẫn trượt và 2 điểm của Q4 là phép đo suy biến |
| **Tổng phần cá nhân** | **56 / 60** | |

### Ba việc tôi biết là còn thiếu

1. **Chưa quét bộ separator** — mới tinh chỉnh `chunk_size`, còn
   `["\n\n", "\n", ". ", " ", ""]` vẫn để mặc định. Thêm `"\nĐiều "` / `"\nArticle "` vào
   đầu danh sách nhiều khả năng thu hẹp được khoảng cách với `HeadingChunker`.
2. **`gold_doc_id` của Q3 và Q5 khai thiếu.** Đáp án hai câu này nằm ở **hai** tài liệu,
   nhưng Contract B chỉ cho khai một. Truy xuất đã đưa nội dung đúng lên hạng 1–2 mà máy chấm
   vẫn báo trượt. Sửa thành `gold_doc_ids` dạng danh sách thì điểm lên 10/10 — nhưng đó là
   sửa **thước đo**, nên tôi để thành vòng riêng thay vì trộn vào vòng đo `institution`.
3. **Môi trường chạy Python 3.14 thay vì 3.11** như `.python-version` quy định.
