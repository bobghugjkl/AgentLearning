# Day 14 复盘笔记 — RAG 评估 + Week 2 收官

## 今天学了什么

### 1. RAGAs 四大评估指标

| 指标 | 含义 | 评估什么 |
|------|------|---------|
| Faithfulness（忠实度） | 回答是否基于文档内容 | 有没有幻觉 |
| Answer Relevancy（答案相关性） | 回答是否回答了问题 | 有没有答非所问 |
| Context Precision（上下文精确度） | 检索内容有多少是有用的 | 有没有引入噪声 |
| Context Recall（上下文召回率） | 需要的信息有多少被检索到 | 有没有漏掉关键内容 |

**哪个最难提升？** Context Recall——正确答案可能分散在文档多处，一次检索很难全部找到。

### 2. LLM-as-Judge（生产环境常用）

用 LLM 来评估 LLM 的回答：

```python
class EvalResult(BaseModel):
    faithfulness_score: float = Field(description="忠实度 0-1")
    relevancy_score: float = Field(description="相关性 0-1")
    faithfulness_reason: str = Field(description="评分理由")
    relevancy_reason: str = Field(description="评分理由")

eval_chain = eval_prompt | model.with_structured_output(EvalResult)

result = eval_chain.invoke({
    "question": question,
    "contexts": contexts,
    "answer": answer,
    "ground_truth": ground_truth,
})
```

**优点：**
- 不需要额外 Embedding 模型
- 评分有理由，可解释
- 灵活，可自定义评估维度

**LLM-as-Judge 的偏见（面试必考）：**
- 位置偏差：偏爱先出现的答案
- 长度偏差：偏爱更长的回答
- 自我偏好：模型偏爱自己风格的回答

**缓解方法：** 随机顺序、多个 judge 投票、CoT 评分。

### 3. Golden Dataset（黄金数据集）

人工标注的问题+标准答案，用于评估：

```python
test_cases = [
    {
        "question": "How long does the project last?",
        "ground_truth": "Three years.",
    },
    ...
]
```

**为什么需要人工标注？** 系统不知道"正确答案是什么"，需要人工提供参考标准。

### 4. 闭包（Closure）

```python
@app.post("/ask/stream")
def ask_stream(body: Question):
    context = "..."  # 外层变量
    
    def generate():           # 内层函数
        for chunk in chain.stream({
            "context": context,        # 直接用外层变量
            "question": body.question  # 不需要传参
        }):
            yield chunk.content
    
    return StreamingResponse(generate(), ...)
```

**内层函数可以自动访问外层函数的变量**，不需要手动传参，代码更简洁。

### 5. Week 2 完整 RAG 系统

```
文档加载（PyPDFLoader）
    ↓
文本切分（RecursiveCharacterTextSplitter）
    ↓
HyDE（口语化问题 → 英文假答案）
    ↓
BM25 检索（精确词语匹配）
    ↓
去重（同页只保留一个）
    ↓
LLM 生成（基于文档内容回答）
    ↓
FastAPI 暴露（普通接口 + 流式接口）
```

---

## Week 2 完整回顾

| 天 | 核心内容 | 关键技术 |
|----|--------|---------|
| Day 8 | 文档加载 + 文本切分 | PyPDFLoader、RecursiveCharacterTextSplitter |
| Day 9 | Embedding + 向量库 | HuggingFaceEmbeddings、Chroma、余弦相似度 |
| Day 10 | 基础 RAG 闭环 | similarity_search、幻觉防御、FastAPI |
| Day 11 | 混合检索 | BM25、EnsembleRetriever、RRF |
| Day 12 | Reranker 重排 | CrossEncoder、精排 vs 粗排 |
| Day 13 | 高阶 RAG | HyDE、多查询改写 |
| Day 14 | RAG 评估 | LLM-as-Judge、Golden Dataset、RAGAs指标 |

---

## 面试考点

**Q：RAGAs 的四个指标分别是什么？**  
答：Faithfulness（忠实度，有没有幻觉）、Answer Relevancy（答案相关性，有没有答非所问）、Context Precision（上下文精确度，检索有没有引入噪声）、Context Recall（上下文召回率，有没有漏掉关键信息）。

**Q：LLM-as-Judge 是什么？有什么偏见？**  
答：用 LLM 来评估 RAG 系统的回答质量，给出分数和理由。偏见包括：位置偏差（偏爱先出现的）、长度偏差（偏爱更长的）、自我偏好（偏爱自己风格的）。缓解方法：随机顺序、多 judge 投票、CoT 评分。

**Q：什么是 Golden Dataset？为什么需要它？**  
答：人工标注的问题+标准答案数据集。系统自己不知道正确答案是什么，需要人工提供参考标准，才能计算召回率、相关性等指标。

**Q：完整 RAG pipeline 有哪些优化手段？**  
答：检索侧——混合检索（BM25+向量）、HyDE假答案、多查询改写、调大k值；排序侧——Reranker精排；生成侧——prompt约束防幻觉、temperature=0；评估侧——LLM-as-Judge、RAGAs指标。

---

## 今日文件结构
```
day14/
├── 01_llm_judge.py     ✅ LLM-as-Judge评估、EvalResult结构化输出
└── 02_complete_rag.py  ✅ Week2收官：BM25+HyDE+去重+FastAPI
```

---

## 下周预告 — Week 3：Agent 进阶
- Day 15：LangGraph 条件边、循环、复杂状态
- Day 16：Human-in-the-Loop（人工审批节点）
- Day 17：工具设计规范、MCP 协议
- Day 18：Plan-and-Execute Agent
- Day 19：Reflexion（失败自反思）
- Day 20：多 Agent Supervisor 模式
- Day 21：Week 3 综合项目