# Day 12 复盘笔记 — Reranker 重排序

## 今天学了什么

### 1. 为什么需要 Reranker
检索阶段（BM25 + 向量）是**粗排**——快速缩小范围，但排名不够精准：
- BM25 只看词频，不理解语义
- 向量把整句压缩成一个数字，信息有损失
- RRF 只是排名融合，没有深度理解

**Reranker 是精排**——对候选块和问题做深度理解，重新打分排序。

### 2. 检索 vs Reranker 分工
```
检索（粗排）：快速从几百个块里筛出 top10-20
                ↓
Reranker（精排）：对 top10-20 深度计算，重新排序
                ↓
取 top3 塞给 LLM
```

**为什么不直接用 Reranker 对所有块排序？**
太慢太贵。10000个块直接精排需要几分钟，用户等不起。先检索缩小范围，再精排，才能兼顾速度和精度。

### 3. CrossEncoder vs Bi-encoder

| | Bi-encoder（向量检索） | CrossEncoder（Reranker） |
|--|----------------------|------------------------|
| 原理 | 问题和文档分别编码成向量，计算距离 | 问题+文档同时输入，输出相关性分数 |
| 速度 | 快（可预先计算文档向量） | 慢（每次都要重新计算） |
| 精度 | 中等 | 高 |
| 适合场景 | 大规模检索（粗排） | 少量候选重排（精排） |

### 4. Reranker 核心代码
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# 构造问题-文档对
pairs = [[question, doc.page_content] for doc in candidates]

# 打分
scores = reranker.predict(pairs)
# scores = [0.8, 0.2, 0.95, 0.1, ...]

# 重新排序
ranked = sorted(
    zip(scores, candidates),
    key=lambda x: x[0],
    reverse=True,  # 分数高的排前面
)

# 取前3个
top_docs = [doc for score, doc in ranked[:3]]
```

### 5. 完整进阶 RAG Pipeline

```
用户问题
    ↓
混合检索（BM25 + 向量，各返回6个）→ ~10个候选
    ↓
Reranker 精排 → top3
    ↓
去重（同页只保留一个）
    ↓
拼接 context
    ↓
LLM 生成回答（流式输出）
    ↓
返回答案 + 来源页码
```

### 6. 基础 RAG vs 进阶 RAG 对比

| | 基础 RAG（Day 10） | 进阶 RAG（Day 12） |
|--|------------------|------------------|
| 检索 | 纯向量 | BM25 + 向量混合 |
| 排序 | 向量相似度 | Reranker 精排 |
| 去重 | ✅ | ✅ |
| 精度 | 中等 | 高 |
| 速度 | 快 | 稍慢 |

---

## 面试考点

**Q：为什么需要 Reranker？检索不够吗？**  
答：检索是粗排，追求速度，精度有限。BM25 只看词频，向量检索有信息损失，RRF 只是排名融合。Reranker 同时深度理解问题和文档的关系，打分更准确，把最相关的内容排到最前面。

**Q：CrossEncoder 和 Bi-encoder 的区别？**  
答：Bi-encoder 把问题和文档分别编码成向量再计算距离，速度快但各自独立计算，理解有限，适合大规模检索粗排；CrossEncoder 把问题和文档同时输入，深度理解两者关系，精度高但速度慢，适合少量候选精排。

**Q：Reranker 为什么不直接对所有文档块排序？**  
答：太慢。10000个块直接精排需要几分钟。先用检索快速缩小到20个候选，再用Reranker精排这20个，整体速度可以控制在秒级。

**Q：完整 RAG pipeline 的步骤？**  
答：混合检索（粗排，BM25+向量，返回top10-20）→ Reranker重排（精排，返回top3）→ 去重（同页只保留一个）→ 拼接context → LLM生成回答 → 返回答案和来源。

**Q：`zip(scores, candidates)` 是什么？**  
答：Python 内置函数，把两个列表逐元素配对。`zip([0.8, 0.2], [doc1, doc2])` 得到 `[(0.8, doc1), (0.2, doc2)]`，方便按分数排序同时保留文档引用。

---

## 今日文件结构
```
day12/
├── 01_reranker.py      ✅ Reranker基础、打分、重排序、对比测试
└── 02_full_pipeline.py ✅ 完整进阶RAG：混合检索+Reranker+去重+LLM
```

---

## 明天预告 — Day 13：高阶 RAG 技巧
- HyDE：让模型先生成"假答案"再检索，解决 query-doc 不对称
- 多查询改写：一个问题改写成多个，提高召回率
- RAG 系统的评估指标