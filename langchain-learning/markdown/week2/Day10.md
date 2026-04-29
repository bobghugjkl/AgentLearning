# Day 10 复盘笔记 — 基础 RAG 系统搭建

## 今天学了什么

### 1. RAG 完整流程
```
用户问题
    ↓
Embedding → 向量 → 向量库检索相关块（k=3）
    ↓
去重（同一页只保留一个）
    ↓
拼接 context（参考资料）
    ↓
context + 问题 → prompt → LLM 生成回答
    ↓
返回答案 + 来源页码
```

### 2. 核心代码结构

```python
def rag_answer(question: str) -> dict:
    # 第一步：检索
    relevant_docs = vectorstore.similarity_search(question, k=4)
    
    # 第二步：去重
    seen_pages = set()
    unique_docs = []
    for doc in relevant_docs:
        page = doc.metadata['page']
        if page not in seen_pages:
            seen_pages.add(page)
            unique_docs.append(doc)
    
    # 第三步：拼接 context
    context = "\n\n".join([
        f"[来源：第{doc.metadata['page']+1}页]\n{doc.page_content}"
        for doc in unique_docs
    ])
    
    # 第四步：调用 LLM
    chain = prompt | model
    response = chain.invoke({
        "context": context,
        "question": question,
    })
    
    return {
        "answer": response.content,
        "sources": [f"第{doc.metadata['page']+1}页" for doc in unique_docs],
    }
```

### 3. RAG 的 system prompt 设计
```python
"""你是一个文档问答助手。
请根据下面提供的文档内容回答用户的问题。
如果文档中没有相关信息，请说"文档中未找到相关信息"。
不要编造文档中没有的内容。

文档内容：
{context}"""
```

**关键约束：**
- 只基于文档内容回答
- 没有相关信息要明确说
- 不要编造 → 防止幻觉

### 4. 为什么要去重
`chunk_overlap=50` 导致相邻块内容高度相似，检索时可能返回同一页的多个块。
去重后同一页只保留一个，避免重复信息干扰模型。

```python
seen_pages = set()
unique_docs = []
for doc in relevant_docs:
    page = doc.metadata['page']
    if page not in seen_pages:
        seen_pages.add(page)
        unique_docs.append(doc)
```

### 5. RAG 的幻觉问题
- **什么是幻觉：** 文档中没有的信息，模型自己编造出来
- **危害：** 用户以为答案来自文档，实际是模型瞎编，严重误导
- **解决：** prompt 明确约束"只基于文档内容回答"

### 6. FastAPI RAG 接口

```python
class Question(BaseModel):
    question: str
    k: int = 3

# 普通接口（带来源）
@app.post("/rag/answer")
def rag_answer(body: Question):
    ...
    return {"answer": response.content, "sources": [...]}

# 流式接口
@app.post("/rag/stream")
def rag_stream(body: Question):
    def generate():
        for chunk in chain.stream(...):
            yield chunk.content
    return StreamingResponse(generate(), media_type="text/plain")
```

**`transfer-encoding: chunked`** 说明流式传输生效。

### 7. temperature=0 用于 RAG
RAG 场景需要稳定输出，不需要创意，所以 temperature=0。

---

## Week 2 RAG 知识串联

```
Day 8  → PyPDFLoader 加载文档，RecursiveCharacterTextSplitter 切分
Day 9  → HuggingFaceEmbeddings 向量化，Chroma 存储和检索
Day 10 → 完整 RAG 闭环，去重，幻觉防御，FastAPI 暴露
```

---

## 面试考点

**Q：RAG 的完整流程是什么？**  
答：离线阶段：文档加载→切分→向量化→存向量库。在线阶段：用户问题→向量化→检索相关块→拼接context→LLM生成回答→返回答案和来源。

**Q：RAG 怎么防止幻觉？**  
答：三个手段：①prompt 明确约束"只基于文档内容回答，没有就说不知道"；②检索质量要高，保证相关内容能被找到；③后处理校验，用 NLI 判断答案是否基于检索内容。

**Q：检索结果为什么要去重？**  
答：chunk_overlap 导致相邻块内容重叠，检索时可能返回同一页多个相似块。去重避免重复信息占用 context 空间，也避免模型受重复信息干扰。

**Q：RAG 的 k 值（检索几个块）怎么选？**  
答：k 太小可能找不到完整答案，k 太大 context 太长消耗 token 多且可能引入噪声。一般3-5，复杂问题可以到8-10。要结合模型上下文限制和文档块大小综合考虑。

**Q：为什么 RAG 要用 temperature=0？**  
答：RAG 要求模型严格基于检索内容回答，需要稳定可重复的输出，不需要创意。temperature=0 确保相同输入得到相同输出，减少随机性带来的幻觉风险。

---

## 今日文件结构
```
day10/
├── 01_basic_rag.py  ✅ 完整RAG闭环、去重、幻觉防御、流式输出
└── 02_rag_api.py    ✅ FastAPI暴露RAG接口、流式和普通两个endpoint
```

---

## 明天预告 — Day 11：召回优化
- 为什么纯向量检索不够用
- BM25 关键词检索 + 向量检索混合
- RRF（倒数排名融合）合并两路结果
- Reranker 重排序提升精度