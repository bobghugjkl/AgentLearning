# Day 13 复盘笔记 — 高阶 RAG 技巧

## 今天学了什么

### 1. 问题：query-doc 表达不对称
用户用口语化中文问，文档用正式英文写：
```
用户问：  "工业博士项目一般持续多长时间？"
文档写：  "The duration of the project corresponds to the duration 
          of the education programme, which is three years."
```
向量检索找不到，因为表达风格差距太大。

---

### 2. HyDE（Hypothetical Document Embeddings）

**核心思路：** 不用原始问题去检索，而是让模型先生成一个"假答案"，用假答案去检索。

```
普通检索：
用户问题 → 向量化 → 检索 → LLM回答

HyDE：
用户问题 → LLM生成假答案 → 假答案向量化 → 检索 → LLM回答
```

**为什么假答案检索更准？**
假答案和文档的表达风格接近（都是正式表述），向量距离更近。

```python
hyde_prompt = ChatPromptTemplate.from_messages([
    ("system", """请根据问题生成一个可能的答案，用英文回答，语气正式。
这个答案不需要完全正确，只需要和文档风格接近。
只输出答案，不要解释。"""),
    ("human", "{question}"),
])

hyde_chain = hyde_prompt | model | StrOutputParser()

# 生成假答案
hypothetical_answer = hyde_chain.invoke({"question": question})

# 用假答案检索
docs = vectorstore.similarity_search(hypothetical_answer, k=3)
```

**实验结果：**
```
原始问题检索 → 第13页（签名要求，完全不相关！）
假答案检索   → 第4页（直接命中项目时长！）
```

**HyDE 的缺点：**
- 多一次 LLM 调用 → 多花钱 + 多延迟
- 依赖假答案质量，模型对领域不熟悉时可能跑偏

**适合场景：**
- 用户问题口语化、模糊
- 文档是专业领域（和日常表达差异大）

---

### 3. 多查询改写（Multi-Query）

**核心思路：** 把一个问题改写成多个不同角度的问题，分别检索，合并结果，提高召回率。

```python
multi_query_prompt = ChatPromptTemplate.from_messages([
    ("system", """把用户的问题改写成3个不同角度的英文问题。
每行一个问题，只输出问题，不要编号和解释。"""),
    ("human", "{question}"),
])

multi_query_chain = multi_query_prompt | model | StrOutputParser()

# 生成多个改写问题
queries = multi_query_chain.invoke({"question": question})

# 每个问题分别检索，合并去重
all_docs = []
for q in queries.strip().split("\n"):
    if q.strip():
        docs = vectorstore.similarity_search(q.strip(), k=2)
        all_docs.extend(docs)

# 去重
seen, unique_docs = set(), []
for doc in all_docs:
    if doc.metadata['page'] not in seen:
        seen.add(doc.metadata['page'])
        unique_docs.append(doc)
```

**实验结果：**
```
原始问题："工业博士薪资待遇怎么样？"

改写后：
- What is the salary range for industrial PhD graduates?
- How does the compensation compare to academic positions?
- What factors influence the salary for industrial PhD holders?

检索结果：第16页（薪资要求）+ 第4页（基金资助薪资）← 都相关！
```

---

### 4. 两种技巧对比

| | HyDE | 多查询改写 |
|--|------|----------|
| 核心思路 | 生成假答案再检索 | 改写成多个问题分别检索 |
| LLM调用次数 | +1次 | +1次 |
| 适合场景 | query-doc表达不对称 | 问题模糊、多义 |
| 召回率提升 | 中等 | 高 |
| 精度影响 | 依赖假答案质量 | 可能引入噪声 |

**组合使用：** 多查询改写 + 每个改写问题用 HyDE，召回率最高，但 token 消耗最多。

### 5. `[:100]` 切片说明
```python
print(doc.page_content[:100])  # 只打印前100个字符，不是文档被截断
```
字符包括空格和标点，英文100个字符约15-20个单词，看起来不多。
完整内容用 `print(doc.page_content)` 查看。

---

## 面试考点

**Q：什么是 HyDE？解决什么问题？**  
答：Hypothetical Document Embeddings，假设文档嵌入。解决用户问题和文档表达风格不对称的问题。让 LLM 先根据问题生成一个假答案，用假答案去检索，因为假答案和文档表达风格接近，向量距离更近，检索更准确。

**Q：HyDE 的缺点是什么？**  
答：两个缺点：一是多一次 LLM 调用，增加延迟和成本；二是依赖假答案质量，如果模型对该领域不熟悉，假答案可能跑偏，反而检索到错误内容。

**Q：多查询改写的原理？**  
答：把用户的一个问题改写成多个不同角度的问题，分别检索，合并去重。因为文档中同一内容可能有不同表达，多角度改写能覆盖更多可能的表达方式，提高召回率。

**Q：RAG 召回率低怎么优化？**  
答：多种手段：①混合检索（BM25+向量）；②HyDE（假答案检索）；③多查询改写；④调大 k 值；⑤减小 chunk_size 让块更精细；⑥换更好的 Embedding 模型（如 BGE-M3）。

---

## 今日文件结构
```
day13/
└── 01_hyde.py  ✅ HyDE假答案检索、多查询改写、对比测试
```

---

## 明天预告 — Day 14：RAG 评估 + Week 2 收官项目
- RAGAs 四大评估指标
- 如何构建 golden dataset
- Week 2 综合项目：把所有 RAG 技术整合成完整系统