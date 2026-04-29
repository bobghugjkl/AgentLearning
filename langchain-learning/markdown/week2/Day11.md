# Day 11 复盘笔记 — 混合检索（BM25 + 向量）

## 今天学了什么

### 1. 纯向量检索的短板
```
用户搜索 "CVR number"（专有名词）
→ Embedding 模型可能没见过这个词
→ 映射到普通向量
→ 和文档里真正包含 "CVR number" 的段落距离很远
→ 明明文档有，但找不到！
```

**向量检索的规律：**
- 擅长：语义相近的表达（"成绩要求" ↔ "grade point average"）
- 不擅长：专有名词、缩写、精确字符串

### 2. BM25 关键词检索
```python
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 3
```

**BM25 vs 向量检索：**
| | BM25 | 向量检索 |
|--|------|---------|
| 原理 | 词频统计 | 语义相似度 |
| 擅长 | 精确词语、专有名词 | 同义表达、语义理解 |
| 不擅长 | 语义理解 | 精确字符串 |
| 需要模型 | 不需要 | 需要 Embedding 模型 |
| 速度 | 快 | 慢（要计算向量） |

### 3. 检索器 vs 直接调方法
```python
# 直接调方法（只能单独用）
docs = vectorstore.similarity_search("query", k=3)

# 包装成检索器（可以和其他组件组合）
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
docs = retriever.invoke("query")
```

**为什么要用检索器：**
- 实现了 Runnable 协议，有 `.invoke()` 方法
- 可以和其他检索器组合（EnsembleRetriever）
- 可以接进 LCEL 管道（`retriever | prompt | model`）

### 4. EnsembleRetriever 混合检索
```python
from langchain_classic.retrievers.ensemble import EnsembleRetriever

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5],  # 两路各占50%权重
)

results = ensemble_retriever.invoke("CVR number requirements")
```

**weights 调整：**
- 文档专有名词多 → 调高 BM25 权重：`[0.7, 0.3]`
- 用户语义表达丰富 → 调高向量权重：`[0.3, 0.7]`

### 5. RRF（倒数排名融合）原理
```
BM25 结果：   [块A 第1名, 块B 第2名, 块C 第3名]
向量结果：    [块C 第1名, 块D 第2名, 块A 第3名]

RRF 打分：分数 = 1/(排名 + 60)

块A：1/61 + 1/63 = 0.0323  ← 两路都靠前，分数高
块C：1/63 + 1/61 = 0.0323  ← 两路都靠前，分数高
块B：1/62 = 0.0161          ← 只有BM25找到
块D：1/62 = 0.0161          ← 只有向量找到

最终排序：块A、块C、块B、块D
```

**60 是常数**，防止排名靠前的块分数过高，平衡两路结果。

### 6. 完整混合检索 + 去重流程
```python
# 混合检索
results = ensemble_retriever.invoke(query)

# 去重（同页只保留第一个）
seen_pages = set()
unique_docs = []
for doc in results:
    page = doc.metadata['page']
    if page not in seen_pages:
        seen_pages.add(page)
        unique_docs.append(doc)
```

---

## 今天遇到的问题

### 问题1：EnsembleRetriever 找不到
**报错：** `cannot import name 'EnsembleRetriever'`  
**原因：** LangChain 1.x 把它移到了 `langchain_classic` 包  
**解决：**
```bash
pip install langchain-classic
```
```python
from langchain_classic.retrievers.ensemble import EnsembleRetriever
```

---

## 面试考点

**Q：为什么不能只用向量检索？**  
答：向量检索对专有名词、缩写、精确字符串效果差。Embedding 模型可能没见过某些专有名词，导致向量映射不准，明明文档有相关内容但找不到。

**Q：BM25 和向量检索的区别？**  
答：BM25 基于词频统计做精确字符串匹配，不需要模型，速度快，擅长专有名词；向量检索基于语义相似度，需要 Embedding 模型，擅长同义表达和语义理解。两者互补。

**Q：什么是 RRF？**  
答：Reciprocal Rank Fusion，倒数排名融合。把多路检索结果按排名打分（1/(排名+60)），两路都靠前的文档分数更高，最终按分数排序合并结果。

**Q：混合检索的 weights 怎么调？**  
答：根据文档特点调整。文档专有名词、缩写多（如技术文档、法律文档）→ 调高 BM25 权重；用户表达多样、语义丰富 → 调高向量权重。一般从 [0.5, 0.5] 开始，根据评测结果调整。

**Q：检索器和直接调方法有什么区别？**  
答：功能相同，但检索器实现了 Runnable 协议，可以和其他组件组合（EnsembleRetriever）、接进 LCEL 管道，更灵活。

---

## 今日文件结构
```
day11/
└── 01_hybrid_search.py  ✅ BM25检索、混合检索、RRF融合、去重
```

---

## 明天预告 — Day 12：Reranker 重排序
- 为什么检索之后还需要重排序
- Cross-encoder vs Bi-encoder 的区别
- 用 BGE Reranker 提升检索精度
- 完整的"检索→重排→生成"pipeline