# Baseline v0 — Trạng thái test trước khi làm TODO

> Chụp trên repo gốc, **chưa sửa một dòng nào** trong `src/`. Output thô:
> [`pytest_v0.txt`](pytest_v0.txt). Đây là mốc để mỗi người đo tiến độ Giai đoạn 1,
> không phải baseline retrieval của Bài tập 3.1 (cái đó cần `compare()` chạy được).

```text
11 passed, 31 failed  (42 test)
Python 3.14 · pytest 9.1.1 · embedder: mock (mặc định)
```

11 test pass sẵn không phải may mắn — chúng chấm phần đề đã cho sẵn (`Document`,
`FixedSizeChunker`, cấu trúc package). Nói cách khác, **mọi test còn lại đều là điểm phải tự
kiếm**, và 30 điểm Hoàn thiện Code là điểm cá nhân lớn nhất của bài.

## Fail nhóm nào, do TODO nào

| Nhóm test | Fail | TODO phải làm | File |
| :-- | :-: | :-- | :-- |
| `TestProjectStructure` | 0/2 | — đã pass | — |
| `TestClassBasedInterfaces` | 0/2 | — đã pass | — |
| `TestFixedSizeChunker` | 0/7 | — đề cho sẵn làm mẫu | `src/chunking.py` |
| `TestComputeSimilarity` | 4 | `compute_similarity` | `src/chunking.py:89` |
| `TestSentenceChunker` | 4 | `SentenceChunker.chunk` | `src/chunking.py:50` |
| `TestRecursiveChunker` | 4 | `RecursiveChunker.chunk` + `_split` | `src/chunking.py:69` |
| `TestCompareChunkingStrategies` | 3 | `ChunkingStrategyComparator.compare` | `src/chunking.py:97` |
| `TestEmbeddingStore` | 8 | `__init__`, `_make_record`, `_search_records`, `add_documents`, `search`, `get_collection_size` | `src/store.py` |
| `TestEmbeddingStoreSearchWithFilter` | 3 | `search_with_filter` | `src/store.py:77` |
| `TestEmbeddingStoreDeleteDocument` | 3 | `delete_document` | `src/store.py:86` |
| `TestKnowledgeBaseAgent` | 2 | `__init__` + `answer` | `src/agent.py` |

## Thứ tự nên làm

Không phải thứ tự trong file, mà thứ tự **mở khóa được nhiều thứ nhất**:

1. **`compute_similarity`** (4 test) — ngắn nhất, và `_search_records` sẽ dùng lại nó.
2. **`SentenceChunker` + `RecursiveChunker`** (8 test) — độc lập, làm được ngay.
3. **`EmbeddingStore`** (14 test tính cả filter + delete) — **khối lớn nhất**, và là thứ
   `scripts/run_benchmark.py` của R3 gọi tới. Chưa xong phần này thì đến Giờ 3 không chạy
   được benchmark, tức là mất luôn phần điểm nhóm chứ không chỉ điểm cá nhân.
4. **`ChunkingStrategyComparator.compare`** (3 test) — cần cả ba chunker xong trước.
5. **`KnowledgeBaseAgent`** (2 test) — ít test nhất, và benchmark chỉ cần nó ở cột "câu trả
   lời của agent" khi chấm rubric 2 điểm.

Làm `store.py` trước `agent.py`: benchmark cần store, agent chỉ ảnh hưởng một phần điểm.

## Cách tự đo tiến độ

```bash
.venv\Scripts\python.exe -m pytest tests/ -q --tb=no
```

Mốc: **11 → 42**. Ai chưa đạt 42/42 thì số benchmark của người đó không được dùng làm bằng
chứng (điều kiện ở [docs/CONTRACTS.md §3](../../docs/CONTRACTS.md#3-contract-c--bảng-kết-quả-benchmark-quan-trọng-nhất)) —
store sai thì mọi con số phía sau đều vô nghĩa.

## Hai điều cần sửa về môi trường

1. **Baseline này chạy trên Python 3.14, lab chuẩn là 3.11** (`.python-version`). 42 test được
   kiểm trên 3.11; nên cài `py -3.11` rồi dựng lại `.venv` trước khi lấy số làm bằng chứng.
2. Baseline này dùng **mock embedder** — đúng cho unit test, nhưng Giai đoạn 2 phải đổi sang
   `EMBEDDING_PROVIDER=local`.
