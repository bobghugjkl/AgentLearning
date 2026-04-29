# 从 PolySeg 到 Agent 工程师的 LangChain 进阶地图

**先说结论：你在一个学历不是主要瓶颈的赛道。** 2025-2026 年中国 LLM 应用/Agent 工程方向正处于红利期——字节、阿里、美团、小红书的 HC 管够，AI 应用后端和 Agent 工程岗**对 211 硕士非常友好**，应届总包 30-55 万是常规水平。你手里的 CV 背景（PolySeg 息肉分割 + YOLOv8 刹车片检测）不是包袱而是**差异化武器**：大多数竞争者只会调 API，而你能把传统 DL 模型包装成 Agent 工具。你担心的微软/亚马逊确实卡学历，但我们本来也不去那——这份路线专门瞄准**HC 多、看作品集、对学校相对宽容**的方向。全文按"市场→路线→面经→项目→资源"展开，每天 1-2 小时的节奏，不上不下地把你带到能面 Agent 岗的位置。

---

## 一、市场真相：为什么现在入场正当时

### 对 211 硕士最友好的三条赛道

2025 年猎聘《AI 技术人才供需报告》显示 AI 技术岗硕博需求占 47%，但这个数字被"算法岗"严重拉高。**一旦把视线移到 LLM 应用/Agent 工程方向，学历要求立刻松动。** 核心原因是：应用岗考察的是 Python 工程能力、系统设计、LangChain 生态熟悉度、RAG 全链路落地，而不是顶会论文。

下表是按 HC 数量、门槛友好度、薪资天花板综合评估的**三条推荐赛道**：

| 方向 | 招聘量 | 学历门槛 | 核心技能 | 1-3 年薪资中位 |
|------|:-:|:-:|------|:-:|
| **AI 应用后端（Python/Go + LLM）** | ⭐⭐⭐⭐⭐ | 本科/211 硕 | FastAPI + LangChain + 向量库 | 25-40K·14-16 薪 |
| **Agent 工程师** | ⭐⭐⭐⭐⭐ | 211 硕 | LangGraph + MCP + 多 Agent | **30-50K·14-16 薪** |
| **RAG 工程师** | ⭐⭐⭐⭐ | 本科/211 硕 | 解析+切片+Embedding+Rerank | 25-45K·14-16 薪 |

对比之下，**纯大模型算法岗**（预训练/RLHF/多模态研究）应届博士为主，DeepSeek/Kimi 社招直接挂"博士优先，硕士需破格条件"，性价比对你来说极低。**这不是放弃梦想，是选赛道**——Agent 工程师两年经验后往架构师方向走，天花板 60-80 万，不比算法岗差。

### 该瞄准哪些公司

**冲刺档（HC 最多、学历相对宽容）**：字节（豆包/Coze/火山引擎 Agent 团队）、阿里（百炼/通义应用开发）、美团（大模型应用后端，40-70K·15 薪）、腾讯（元宝/混元 Agent）。这些大厂 2025 Q1 放出的大模型岗同比增长 60%，硕士实习转正路径清晰。

**稳妥档**：小红书（后端 AI 侧 52-62w 总包）、京东 JoyAgent、快手可灵、网易伏羲、蚂蚁智能体平台。这批公司面试强度低一档但技术栈一样，非常适合保底。

**隐藏矿区**：**Dify、FastGPT、RagFlow、Bisheng、DB-GPT** 这些开源项目背后的公司（LangGenius、珑珑科技、InfiniFlow 等），团队 30-200 人，**薪资 20-40K、本科可投、看 GitHub 贡献**——给这些项目贡献 PR 本身就是求职筹码。

**别硬冲**：DeepSeek、Kimi 算法岗（2025 起明确"硕士需顶会论文"）、微软 MSRA、NVIDIA 中国（基本只要 985/海外 + 硕博）。

### 日本市场：N2 日语 + 英语 Business 是甜蜜点

既然你在学日语，这是一个**非常现实的 B 计划，甚至可以是 A 计划**。日本对中国 211/985 硕士的态度和中国某些大厂相反——**学历认可度高、缺口大、签证友好**。

**关键事实**：清华、北大、复旦、上交、浙大、中科大、南大等大量中国 211/985 属于高度人材签证"**加点对象大学**"，直接 +10 分；加上硕士学位（20 分）、AI 工程师年收（10-15 分）、年龄 29 岁以下（15 分）、N2（10 分），你基本**轻松跨过 70 分门槛**，3 年拿永住。日本经产省预测 2030 年 IT 人才缺口 79 万，Sakana AI、Preferred Networks、ELYZA 这类公司长期在招。

**对中国人最友好的公司（英语 Business 可工作）**：**Mercari**（官方英语环境，历史上去清北办过 hackathon）、**Rakuten 楽天**（公司官方语言英语，不要求日语）、**LINE Yahoo**（40+国籍员工，双语 JD）、**Woven by Toyota**、**PayPay**、**Cookpad**。其中 Mercari 2025 年 12 月新发布多个 LLM 岗（Software Engineer Backend AI/LLM、ML Research Engineer AI/LLM 等），Cookpad Principal Applied AI 开到 ¥16M-29M（约合 80-145 万人民币）。

**日语 N1 才能进的档**：ELYZA（东大松尾研系、日语 LLM 龙头）、Preferred Networks（自研 PLaMo 2.0）、CyberAgent AI Lab、SB Intuitions、Stockmark。这些是"日语 LLM 国家队"，日语强的话含金量极高。

**求职渠道优先级**：TokyoDev（tokyodev.com，质量最高，每周 newsletter）、Japan Dev（japan-dev.com，272 个精选无日语要求岗）、LinkedIn Japan、Wantedly、Findy（GitHub 评分系）、ASIA to JAPAN（针对中国 211/985 新卒直招）。

**薪资对比要诚实**：日本 AI 工程师 1-3 年中位 600-1200 万日元（约 30-60 万人民币），**低于中国一线大厂 AI 岗**；但外资在日（OpenAI/Anthropic Tokyo）可达 2000-4000 万日元。日本的价值是 work-life balance + 海外履历 + 永住路径，不是薪资峰值。

### 学校这件事，说句真话

你是 211 硕士，2029 年毕业，目标 Agent 工程岗——**学校不是你的短板，作品集的厚度才是**。大厂面试官筛简历的顺序是：相关项目 > 实习 > 学校 > GPA。两个 star：（1）你的本科毕设是双分支分割网络，不是调包作品，说明你能啃 paper 写代码；（2）YOLOv8 刹车片项目是完整 pipeline 不是 demo，说明你有工程落地意识。这两点加上接下来 12-18 个月的 LangChain 投入 + 2-3 个高质量 Agent 项目，**你的简历会比很多 985 但只有课程作业的同学硬得多**。说白了：你焦虑的是学校，面试官焦虑的是招不到能干活的人。

---

## 二、LangChain 学习路线（每天 1-2 小时，约 14 周）

### 路线设计哲学

你每天 1-2 小时、不设时间上限、希望扎实——这个节奏最合适的是**14 周闭环**（约 90-100 天），覆盖阶段 0-6。不是死抠日期，慢一点没关系，**每天必须有代码产出**比每天看文档更重要。下文每个阶段标 "Week X-Y"，每天标 "Day N"，你按自己节奏走就行。

技术栈锚定 **LangChain 1.0 + LangGraph 1.0**（2025 年 9 月发布）。老教程里的 `LLMChain`、`AgentExecutor`、`RetrievalQA`、`initialize_agent` **全部废弃**，不要学了——面试官一听就知道你看的是 2023 年的教程。新统一入口是 `langchain.agents.create_agent` 和 `langgraph.prebuilt.create_react_agent`。

### 阶段 0：LLM API 调用基础（Week 1，7 天）

你 DeepSeek API 调过但"基本零基础"，这个阶段把底子夯实。别跳过——面试时一个"流式输出怎么实现"就能筛掉一半候选人。

**Day 1：OpenAI-compatible API 本质**
- 内容：Chat Completion 协议、messages 数组结构（system/user/assistant/tool）、temperature/top_p/max_tokens 语义、DeepSeek/通义/Kimi 都用同一套协议的历史原因
- 重点：**理解"所有国产模型都兼容 OpenAI 协议"**，这是你后续所有代码能一行切换模型的基础
- 必练：用 `openai` SDK 分别调 DeepSeek、通义（base_url 指向 dashscope）、Kimi、智谱，完成同一个"翻译助手"任务，对比输出
- 难点：base_url 路径差异（有的要 `/v1`、有的不要）；api_key 环境变量管理（用 `python-dotenv`）
- 面试考点："DeepSeek 和 OpenAI 的 API 有什么区别？"（答：协议一致、仅端点/密钥/模型名不同，这就是国产替代友好的根因）

**Day 2：流式输出与 SSE**
- 内容：`stream=True` 的返回结构、delta 拼接、Server-Sent Events 协议、首 token 延迟（TTFT）vs 每 token 延迟（TPOT）概念
- 重点：**生产环境必上流式**，首 token < 1s 是用户体验红线
- 必练：写一个命令行聊天程序，逐字打印回复；再用 FastAPI 暴露为 SSE 端点（`text/event-stream`），用 curl 测试
- 难点：Nginx 反代时要关 buffer（`X-Accel-Buffering: no`）、前端 EventSource 断线重连
- 面试考点："SSE 和 WebSocket 选哪个？"（答：单向推流用 SSE 简单、HTTP 鉴权/CDN 友好；多轮交互用 WS）

**Day 3：Function Calling 原理**
- 内容：tools 参数的 JSON Schema、tool_choice、模型返回的 `tool_calls`、多轮调用的 messages 拼接
- 重点：**Function Calling 是模型层协议，不依赖任何框架**；LangChain/LangGraph 只是封装
- 必练：不用 LangChain，纯 openai SDK 实现一个"查天气 Agent"——手动解析 tool_calls、执行函数、把结果作为 tool message 回给模型、直到 finish_reason=stop
- 难点：多个 tool_call 并行返回时的 message 顺序；tool_call_id 必须对应
- 面试考点："手写一个不用 LangChain 的 ReAct loop"（字节曾考过，考察你对底层的理解）

**Day 4：异步与并发**
- 内容：`AsyncOpenAI`、`asyncio.gather`、连接池、限流退避（tenacity 库）
- 重点：你学过多线程多进程，**LLM 场景 I/O 密集首选 asyncio**，不要用线程池
- 必练：批量处理 100 条新闻标题做情感分类，用 `asyncio.gather` 控制并发度（semaphore 限 10），对比串行耗时
- 难点：异步环境里的 rate limit 触发、指数退避
- 面试考点：高并发 LLM 服务的设计

**Day 5：Tokenizer 与成本**
- 内容：tiktoken/transformers tokenizer、中英文 token 比例差异、input/output 定价差异、cache hit 机制（DeepSeek、Anthropic prompt caching）
- 重点：**token 不是字，中文平均 1.5 字/token，英文 0.75 词/token**
- 必练：写一个成本估算器，给定 prompt 和模型，输出预估费用；用 DeepSeek 开启 prompt cache 对比命中前后成本
- 难点：tokenizer 与模型对应（DeepSeek 不用 tiktoken）
- 面试考点：成本优化策略

**Day 6：结构化输出**
- 内容：JSON mode、Structured Output（response_format + json_schema）、Pydantic 模型、函数调用 vs JSON mode 差异
- 重点：**生产里永远要求模型输出 JSON**，自由文本解析是故障之源
- 必练：用 Pydantic 定义 `ProductInfo(name: str, price: float, tags: list[str])`，让模型从段落抽取结构化信息，错误重试
- 难点：模型有时生成带 markdown 代码块的 JSON，要用正则清理
- 面试考点：怎么让 LLM 输出稳定的 JSON？

**Day 7：阶段小项目 —— 命令行多模型聊天工具**
- 整合 Day 1-6 知识，做一个支持模型切换（`/model deepseek-chat`）、流式输出、历史上下文、JSON 抽取指令（`/extract`）的命令行工具
- 代码放 GitHub，写个 README——你的第一个开源项目，后面简历可以挂

### 阶段 1：LangChain 核心与 LCEL（Week 2-3，14 天）

你已经懂了底层，现在看看 LangChain 怎么抽象它。**千万不要学 `LLMChain`**——那是 2023 年的东西。

**Day 8：LangChain 包结构与 init_chat_model**
- 内容：langchain-core / langchain / langchain-community / langchain-openai 分包逻辑；`init_chat_model("deepseek-chat", model_provider="deepseek")` 一行接入
- 必练：用 `init_chat_model` 分别初始化 5 个国产模型（DeepSeek、通义、Kimi、智谱、豆包），写一个"同一问题多模型横评"脚本
- 难点：`langchain-deepseek` 包是单独的、`ChatTongyi` 在 community 包里
- 面试考点：LangChain 的分包设计为什么这么做？（答：核心轻量化、provider 独立升级、避免巨型依赖）

**Day 9：Runnable 协议**
- 内容：`invoke`/`stream`/`batch`/`ainvoke`/`astream` 五大方法、`RunnableLambda`、`RunnableParallel`、`RunnablePassthrough`
- 重点：**Runnable 是 LangChain 的灵魂**，万物皆 Runnable
- 必练：把一个普通函数 `def clean(text): return text.strip().lower()` 包成 `RunnableLambda`，接进一条 chain
- 面试考点："LCEL 背后的 Runnable 协议解决什么？"（答：统一接口 → 自动并发、流式、重试、观测）

**Day 10：LCEL 管道**
- 内容：`prompt | llm | parser` 组合、`RunnableParallel({"a": x, "b": y})` 并行分支
- 重点：**LCEL 在 LangChain 1.0 被弱化**（简单场景直接 `model.invoke()`），但仍是 LangGraph 节点内部主力
- 必练：写一个"同时做摘要和翻译"的并行 chain，比较串行/并行耗时
- 难点：管道里的类型传递，Pydantic v2 vs v1 坑
- 面试考点：LCEL 什么时候还用？什么时候不用？

**Day 11：Prompts**
- 内容：`ChatPromptTemplate`、`MessagesPlaceholder`、`from_messages` 的 tuple 语法、`partial`、Prompt Hub（`hub.pull`）
- 必练：写一个带 few-shot 的翻译 prompt，动态拼上过去 3 轮历史
- 面试考点：system prompt 泄露怎么防

**Day 12：Output Parsers**
- 内容：`StrOutputParser`、`JsonOutputParser`、`PydanticOutputParser`、`.with_structured_output(Schema)`（推荐）
- 重点：**`with_structured_output` 优先级最高**，底层自动用模型原生 structured output 能力
- 必练：用 Pydantic 模型抽取一段新闻中的人名、机构名、事件
- 面试考点：JSON 解析失败怎么办？（答：with_retry + fallback parser）

**Day 13：Runnable 的高级玩法**
- 内容：`.with_retry`、`.with_fallbacks`、`.with_config(tags=...)`、`.bind(temperature=0)`
- 必练：构造一条"主用 DeepSeek，失败 fallback 到 Kimi"的 chain，故意把 base_url 设错测试
- 面试考点：生产级容错怎么做

**Day 14：Memory 的演进史**
- 内容：旧 `ConversationBufferMemory`/`SummaryMemory`/`EntityMemory`（**已废弃但面试会问**）、新做法用 LangGraph Checkpointer
- 重点：**面试讲得出老的，写代码用新的**
- 必练：用 LangGraph 最简 StateGraph 实现一个有记忆的聊天机器人（SqliteSaver）
- 面试考点：ConversationBuffer/Summary/Entity/VectorStore Memory 区别？

**Day 15-17：LangChain 文档加载与处理**
- Day 15：Document Loaders（PDF、网页、Notion、飞书）+ Unstructured 深度解析；难点是**扫描版 PDF**要走 OCR
- Day 16：Text Splitters —— RecursiveCharacterTextSplitter、MarkdownHeaderTextSplitter、SemanticChunker（基于嵌入相似度切）、Late Chunking（2024 新范式，嵌入后切）
- Day 17：Embeddings —— OpenAI、BGE-M3、**Qwen3-Embedding-0.6B/4B/8B**（Apache 2.0，2025-06 MTEB 多语言榜第一，中文 RAG 首选）；用 HuggingFace 下载本地跑

**Day 18-21：第一个 RAG Demo（阶段里程碑）**
- Day 18：搭起最小 RAG——LangChain loader 读 PDF、RecursiveSplitter 切、BGE-M3 embed、Chroma 存、`.similarity_search` 查
- Day 19：加上 LLM 生成环节，完成"问答闭环"；用 LCEL `{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()`
- Day 20：把它用 FastAPI 暴露为 API，支持流式
- Day 21：上传到 GitHub，**第二个开源项目**

### 阶段 2：RAG 系统深度攻坚（Week 4-6，21 天）

面试 RAG 八成考这里——"百万级文档怎么做？"别背答案，写代码。

**Day 22-24：向量库选型与实战**
- Day 22：Chroma（原型）、Qdrant（10-50M 生产级 Rust 栈）、Milvus（十亿级分布式）、pgvector（已有 PG 的小规模）、FAISS（非 DB 但 GPU 最强）——每个都跑通一遍
- Day 23：**HNSW / IVF_PQ / DiskANN 索引原理**——HNSW 小图邻居跳转、IVF 聚类倒排、PQ 量化。用 Qdrant 建不同索引对比召回率/延迟
- Day 24：**元数据过滤**（Qdrant filter-first 特性）、多租户方案
- 面试考点："Milvus vs Qdrant vs pgvector 怎么选？"

**Day 25-27：Chunking 策略**
- Day 25：固定窗口 + overlap、RecursiveCharacterTextSplitter 的层次分隔符逻辑
- Day 26：Semantic Chunking（相邻句嵌入相似度突变切）、Markdown 标题保留
- Day 27：**Parent-Child Chunking**（小块检索大块喂 LLM，`ParentDocumentRetriever`）、表格/代码单独处理
- 必练：同一份 PDF 用 4 种策略切，人工评估哪种更保语义
- 面试考点：chunk size 怎么定？（答：取决于 embedding 最大长度 + LLM 上下文预算 + 问题粒度，常见 300-800 token）

**Day 28-30：召回与重排**
- Day 28：**Hybrid Search** —— BM25 (Elasticsearch 或 rank_bm25 库) + dense vector，**RRF (Reciprocal Rank Fusion)** 融合
- Day 29：**Reranker** —— `bge-reranker-v2-m3`（免费中文强）或 **Qwen3-Reranker**（2025 SOTA）；cross-encoder vs bi-encoder 区别
- Day 30：实测——T2-RAGBench 上 hybrid + rerank 把 Recall@5 从 0.695 推到 0.816
- 面试考点："为什么不能只上向量库？"（答：向量召回表达不对称 query 差、BM25 补长尾，rerank 去噪声）

**Day 31-33：Query 侧优化**
- Day 31：**Query Rewriting** 处理口语化；**HyDE**（让 LLM 生成"假答案文档"再去 embed），解决 query 和 doc 表达风格不对称
- Day 32：**Multi-Query Retriever**（生成 3-5 条改写并 RRF 合并）、**Step-back Prompting**（先抽象问题再检索，适合多跳）
- Day 33：**Query Routing**（判断走 FAQ / 向量 / SQL / web 搜索）
- 面试考点：用户问"苹果多少钱"怎么处理歧义（水果 vs 公司）？

**Day 34-36：高阶 RAG 范式**
- Day 34：**Self-RAG** —— 训练 LLM 用 reflection tokens 自决定是否检索；论文 arXiv:2310.11511
- Day 35：**CRAG (Corrective RAG)** —— 检索质量低时触发 Web 搜索纠正；arXiv:2401.15884
- Day 36：**RAPTOR** —— 递归聚类摘要构多粒度树；**GraphRAG**（微软，实体-关系图 + 社区摘要）——跑一遍 `graphrag` 包，感受 token 成本
- 面试考点：GraphRAG vs 传统 RAG vs Agentic RAG 场景差异

**Day 37-39：评估体系**
- Day 37：**RAGAs** 四大指标——Faithfulness（答案是否基于上下文）、Answer Relevancy、Context Precision、Context Recall
- Day 38：**DeepEval**、**TruLens** 对比；自己写 Dataset 跑离线评测
- Day 39：**LLM-as-Judge 偏见**——位置偏差、长度偏差、自我偏好；缓解：随机顺序 + 多 judge + CoT + 校准到人工
- 面试考点："线上 RAG 怎么评？" 答：离线 RAGAs + 在线采纳率/复问率 + 定期人工抽检

**Day 40-42：阶段项目 —— 医学影像报告 RAG（v0.1）**
- 你的差异化王牌之一。索引放射科报告 + 教材，支持"类似病例"检索、引用溯源
- Day 40：数据准备，用 Unstructured 解析报告 PDF，按章节切分
- Day 41：BGE-M3 hybrid 索引 + Qwen3-Reranker；**实现 citation（每句答案标注来源）**
- Day 42：RAGAs 评测跑通，faithfulness > 0.85 才算及格

### 阶段 3：Agent 与工具调用（Week 7-8，14 天）

这是你未来岗位的核心。LangChain 1.0 起 Agent 入口**统一到 LangGraph**，直接按新范式学，不要碰老的 `AgentExecutor`。

**Day 43：Agent 思想起源**
- 论文通读：**ReAct**（Yao 2022, arXiv:2210.03629）Thought-Action-Observation 循环
- 必练：不用任何框架，纯 OpenAI SDK 复现一个 ReAct Agent 解"25 的平方根加 7 的立方是多少"
- 面试考点：ReAct 为什么比 CoT 好？（答：引入外部工具突破模型知识边界）

**Day 44：create_react_agent（LangGraph prebuilt）**
- 内容：`from langgraph.prebuilt import create_react_agent`；最简三行 Agent
- 必练：实现一个"天气 + 股票 + Python 计算"三工具 Agent，测试复合任务
- 难点：tool 名字和 description 对 LLM 理解至关重要
- 面试考点：`bind_tools` 后 Agent 怎么决定调哪个？（答：模型 function-calling 返回 tool_calls 列表，LangGraph ToolNode 默认并行）

**Day 45：Tool 设计规范**
- 内容：`@tool` 装饰器、Pydantic schema 参数、docstring 作为 description、返回值截断、幂等性、对危险操作加人审批
- 重点：**LLM 看的是 description，不是函数名**
- 必练：给同一个工具写 3 种不同 description，对比 Agent 调用正确率
- 面试考点：Tool 设计原则（命名清晰/schema 严格/返回截断/危险操作 HITL）

**Day 46-47：Plan-and-Execute 与 Reflexion**
- Day 46：Plan-and-Execute —— Planner 先出 DAG，Executor 顺序执行，省 token 适合可预估任务
- Day 47：**Reflexion**（arXiv:2303.11366）——失败后 LLM 反思写入 memory 再重试，代码/数学题强
- 必练：用 LangGraph 实现 Plan-Execute 解决多步数学应用题
- 面试考点："ReAct vs Plan-Execute vs Reflexion 怎么选？"

**Day 48：Function Calling / MCP / A2A 三协议**
- 内容：**Function Calling** 是模型层协议；**MCP (Model Context Protocol, Anthropic 2024)** 是 Client-Server 工具/资源标准化；**A2A (Agent-to-Agent)** 是 Agent 间互操作
- 重点：**MCP 是 2025 年面试高频考点**，必须能讲清楚和 Function Calling 的层级关系
- 必练：用 `mcp` Python SDK 暴露一个本地 SQLite 查询服务；用 LangGraph Agent 连接它
- 面试考点：MCP 为什么重要？（答：统一工具生态，避免每个框架重造轮子）

**Day 49-50：实战——自己的 YOLOv8 模型包成 Agent 工具**
- Day 49：把刹车片检测模型用 FastAPI/TorchServe 部署，返回 JSON 格式检测结果
- Day 50：用 `@tool` 包装这个 HTTP 接口，接到 LangGraph Agent；Agent 能根据用户上传图片自动调用 → 查 SOP RAG → 给处置建议
- **这一步做完，简历上一句"将 YOLOv8 工业检测模型工具化为 Agent"就完爆 99% 只会调 API 的人**

**Day 51-52：Memory 工程**
- Day 51：**三层记忆架构**——短期（上下文窗口）、中期（session checkpoint）、长期（向量库 + KV，如 Mem0/Zep）
- Day 52：Context 溢出策略——滑动窗口、LLM summary 压缩、重要性过滤、工具结果截断
- 面试考点："Agent 上下文满了怎么办？"

**Day 53-54：Prompt Engineering 进阶**
- Day 53：CoT、Zero-shot CoT、Self-Consistency（多采样投票）、Tree of Thoughts；**R1/o1 已内化 CoT 外层不要再加**
- Day 54：**Prompt 注入防御**——直接注入、间接注入（RAG 文档藏指令）、越狱；防御：数据指令分离 + 分类器 + HITL + 最小权限 tool
- 面试考点：Prompt 注入类型与防护

**Day 55-56：阶段项目 —— 医疗多模态 Agent v0.1**
- 你的差异化王牌项目。上传内窥镜图 → Agent 调 **PolySeg** 分割 → 调 Qwen2.5-VL 描述病灶 → RAG 检索临床指南 → 结构化诊断
- Day 55：把 PolySeg 用 FastAPI 部署返回 mask 坐标 + 置信度
- Day 56：LangGraph 搭 Agent，先单工具跑通流程

### 阶段 4：LangGraph 多智能体（Week 9-10，14 天）

**这是 2025-2026 大厂面试的重头戏**，也是你简历最有分量的加分点。

**Day 57：StateGraph 核心概念**
- 内容：`TypedDict` 状态 + `Annotated[list, add_messages]` reducer、`add_node`、`add_edge`、`add_conditional_edges`、`START`/`END`
- 重点：**节点只返回增量更新，Reducer 定义合并策略**
- 必练：从零手写一个两节点图（输入 → LLM → 输出）
- 面试考点："为什么用 TypedDict + Annotated[list, add_messages]？" 答：并行写入时的合并策略，防止覆盖

**Day 58：条件边与循环**
- 内容：`add_conditional_edges(node, routing_func, {"continue": node_a, "end": END})`；**ReAct 的本质就是一个带条件回边的循环**
- 必练：手写一个不用 prebuilt 的 ReAct Agent，完全自己控制 state 转移
- 面试考点：LangChain vs LangGraph 区别（答：顺序链 vs 支持循环的状态图）

**Day 59：Checkpoint 机制**
- 内容：`InMemorySaver`（测试）、`SqliteSaver`（本地）、`PostgresSaver`（生产）；`thread_id + checkpoint_id` 回溯
- 重点：**每个 super-step 自动保存 StateSnapshot**，支持时间旅行、崩溃恢复、HIL
- 必练：跑一个长对话，中途 kill 进程，用 thread_id 恢复继续
- 面试考点：生产环境选哪种 saver？（答：PostgresSaver，并发要 parent_ts 乐观锁或 sticky session）

**Day 60：Human-in-the-Loop**
- 内容：`interrupt()` 暂停 → 外部系统取 state → 人审核 → `Command(resume=value)` 继续
- 必练：在你的医疗 Agent 里加入"医生确认"节点，Agent 给出初诊建议后等待医生批准才写入病历
- 面试考点：HITL 怎么实现？生产怎么持久化？

**Day 61：Streaming 模式**
- 内容：`graph.astream(input, stream_mode="messages"/"updates"/"values"/"custom")`、每种模式的使用场景
- 必练：前端用 SSE 接"messages"流，实时展示中间步骤
- 面试考点：LangGraph 的几种 stream mode 区别

**Day 62-63：多 Agent 协作模式**
- Day 62：**Supervisor 模式**（`langgraph-supervisor`）——路由 Agent + N 个 Worker；最常见的生产模式
- Day 63：**Swarm 模式**（`langgraph-swarm-py`）——`create_swarm([alice, bob], default_active_agent="Alice")` 通过 handoff tool 动态移交
- 必练：用 Supervisor 搭一个"研究助手 + 代码助手 + 绘图助手"三 Agent 系统
- 面试考点：多 Agent 的优势和坑（优势：专业化、解耦；坑：通信开销、错误传播、token 爆炸）

**Day 64：Subgraphs**
- 内容：已编译的图可以作为节点嵌入父图——**分层 Agent 架构的基石**
- 必练：把 Day 62 的 Supervisor 系统作为子图，外层再加入 Router
- 面试考点：为什么需要 Subgraphs？

**Day 65：Send API 并行**
- 内容：`Send("node_name", state)` 在 conditional edge 里动态 spawn 多个并发节点——map-reduce 风格
- 必练：批量翻译 50 段文本，并发 10 路
- 面试考点：map-reduce 怎么在 LangGraph 里实现

**Day 66：Deep Agents**
- 内容：`deepagents` 包（Claude Code 启发）——**内置 planning tool + virtual filesystem + subagent spawning**；适合长上下文研究/代码任务
- 必练：用 deepagents 写一个"调研某技术主题并输出报告"的 Agent
- 面试考点：Deep Research 类产品背后的架构思路

**Day 67：LangGraph Studio 可视化调试**
- 内容：`langgraph dev` 本地启动，浏览器打开 Studio，**单步执行、编辑 state、fork thread**
- 必练：在 Studio 里调你的医疗 Agent，刻意制造失败观察回溯
- 面试考点：你怎么调试复杂 Agent？（答：Studio + LangSmith trace，不是 print）

**Day 68-70：阶段项目 —— 多 Agent 研究助手**
- 三天搭一个 mini Deep Research，对标 OpenAI Deep Research
- Day 68：Fork `open-deep-research`（langchain-ai 官方，Deep Research Bench #6），理解 Supervisor-Researcher 架构
- Day 69：改造——中文源（知网/arxiv 中文）+ PDF 解析 + DeepSeek-R1 做 reasoning + Qwen-Turbo 做 summary
- Day 70：前端接 `agent-chat-ui`，展示 tool-call 可视化，**这个项目可以直接挂简历**

### 阶段 5：LangSmith 与生产化（Week 11-12，14 天）

面试官会问"线上真实效果怎么评估的？"——没有这一章你就答不出来。

**Day 71-72：LangSmith Tracing**
- Day 71：注册、设 `LANGSMITH_API_KEY` + `LANGSMITH_TRACING=true`，所有 LangChain/LangGraph 代码自动有 trace
- Day 72：看 trace 里的 token 消耗、延迟瀑布图、tool 调用序列；用 `@traceable` 装饰自定义函数
- 面试考点：你怎么排查 Agent 卡在某步？（答：LangSmith trace 看具体哪个节点超时/报错）

**Day 73-75：LangSmith Evaluation**
- Day 73：创建 Dataset（输入+参考输出）、跑 `evaluate()` API
- Day 74：写自定义 evaluator（correctness、faithfulness、toxicity）；LLM-as-judge 的 prompt 设计
- Day 75：**Pairwise 评测**——两版 prompt 直接对比胜率；**Regression 评测**——每次改 prompt 跑数据集看有没有倒退
- 面试考点：prompt 改了怎么保证不回退？（答：dataset + regression eval）

**Day 76：Prompt Hub**
- 内容：`hub.pull("owner/prompt-name")`、版本化管理、团队协作
- 必练：把你的医疗 Agent 核心 prompt 上传 hub，做版本管理
- 面试考点：生产环境怎么管理 prompt？

**Day 77-79：FastAPI 生产化集成**
- Day 77：用你熟的 FastAPI 暴露 LangGraph Agent，**SSE 流式**（`EventSourceResponse`）
- Day 78：**并发与限流**——`asyncio.Semaphore`、Redis 令牌桶、按用户 token 配额
- Day 79：**错误处理与降级**——`with_fallbacks` 到小模型；熔断（failed > 阈值直接拒）；超时（asyncio.wait_for）
- 面试考点：QPS 1000 的 LLM 服务设计

**Day 80：缓存与成本优化**
- 内容：**语义缓存**（GPTCache，命中率 30%+）、**Prompt Caching**（DeepSeek 自动/Anthropic cache_control）
- 必练：给你的 RAG 接入 GPTCache，测命中率和节省
- 面试考点：成本减半怎么做？

**Day 81：向量库的生产运维**
- 内容：增量索引 vs 全量重建、文档级 hash 比对、`upsert` 或软删除、**版本化 collection 切换**
- 必练：给医疗 RAG 加一个定时增量更新脚本
- 面试考点：脏数据怎么清？索引怎么平滑切换？

**Day 82：可观测性栈**
- 内容：LangSmith + Prometheus（QPS、TTFT、TPOT）+ Grafana + Loki 日志；开源替代 Langfuse
- 必练：给医疗 Agent 加 Prometheus metrics，本地跑 Grafana dashboard
- 面试考点：上线后怎么监控？

**Day 83：部署选项对比**
- 内容：**LangGraph Platform**（官方，Redis + PG，支持长跑任务/Cron）、自建 FastAPI + K8s HPA、Modal/Replicate 无服务器
- 必练：把 Agent 打包 Docker，用 docker-compose 起 PG + Redis + Agent
- 面试考点："长时间运行的 Agent 任务怎么部署？"（答：LangGraph Platform 或 Celery + Redis）

**Day 84：安全加固**
- 内容：API Key 轮换、敏感信息脱敏、Llama Guard 内容审核、最小权限 tool、审计日志
- 面试考点：LLM 产品合规怎么做？

### 阶段 6：综合实战（Week 13-14，14 天）

选一个大项目打磨到可以挂简历、可以面试深挖、可以开源博客的程度。**建议选"医疗多模态 Agent"打完全场**——这是你独有的差异化。

**Day 85-90：医疗多模态 Agent v1.0（6 天迭代）**
- Day 85：架构重构——LangGraph Supervisor（Router + PolySeg Agent + VLM Agent + RAG Agent + Critic）
- Day 86：工具化——PolySeg（息肉分割返回 mask 坐标）、YOLOv8（如有病灶检测）、Qwen2.5-VL（病灶描述）全部用 `@tool` 统一接口
- Day 87：RAG 增强——临床指南库（NCCN / 中华医学会）+ 历史病例库；GraphRAG 实体图（疾病-部位-征象）
- Day 88：HIL 节点——医生审核后才生成正式报告；LangSmith trace 全链路
- Day 89：FastAPI + Next.js（fork agent-chat-ui）前端；SSE 流式 + mask 可视化
- Day 90：RAGAs + 自建 golden set 评测，写技术博客

**Day 91-93：第二个项目——你的选择**
- 选项 A：**刹车片巡检 Agent**（工业 AI，国产化栈 DeepSeek + MCP 接 MES）
- 选项 B：**多 Agent 学术助手**（对标 Deep Research，展示 Supervisor/Swarm）
- 选项 C：**代码 Agent**（用 deepagents，展示你懂 Claude Code 底层）
- 3 天出 MVP，后续空闲时间持续迭代

**Day 94-98：面试准备周**
- Day 94：把本路线所有面试考点过一遍，在本子上手写答案
- Day 95：模拟"项目深挖"——对着镜子讲 PolySeg、YOLOv8、医疗 Agent、RAG 项目各 5 分钟
- Day 96：刷 LeetCode 中等题（大模型岗一般不考 hard，但滑窗/DFS/二分要熟）
- Day 97：系统设计——手画"百万文档 RAG"、"QPS 1000 LLM 服务"、"多 Agent 协作"架构图
- Day 98：准备 3 个自己的反问（技术栈、团队结构、晋升路径）

---

## 三、面试题库：真题与标答要点

### LangChain / LangGraph 原理（高频）

**Q1：LCEL 到底解决什么？`|` 背后的 Runnable 协议是什么？**（阿里云/字节 Coze）
答：所有组件实现 `Runnable` 接口统一 invoke/stream/batch/ainvoke，`__or__` 重载把 prompt-model-parser 串成 DAG；自动支持 `RunnableParallel` 并发、`.with_retry`、`.with_fallbacks`、LangSmith trace 注入。LangChain 1.0 起简单场景可直接 `model.invoke()` 不强推 LCEL，但 LangGraph 节点内仍是主力。

**Q2：LangGraph 与 LangChain 的本质区别？什么时候必须用 LangGraph？**（腾讯混元/阿里通义）
答：LangChain 是顺序链（DAG），LangGraph 是 State Graph 支持分支/循环/回溯。带循环的 Agent（ReAct）、多工具、带记忆、HIL、多 Agent 协作必须用 LangGraph。

**Q3：LangGraph 的 State 为什么用 `TypedDict + Annotated[list, add_messages]`？Reducer 有何作用？**（字节 AML）
答：节点只返回增量更新，Reducer（`add`、`add_messages`）定义多字段并行写入时的合并策略防止覆盖；支持私有/共享 channel 隔离。

**Q4：Checkpoint 机制怎么实现"时间旅行"和崩溃恢复？生产选哪种 saver？**（阿里云/美团）
答：每个 super-step 自动保存 StateSnapshot（channel_values、versions、next、parent_config），通过 `thread_id + checkpoint_id` 回溯；生产用 `PostgresSaver` 或 `RedisSaver`，`MemorySaver` 仅测试；并发用 parent_ts 乐观锁或 sticky session。

**Q5：Memory 的几种实现差异？**（快手提前批）
答：旧 API——Buffer 全量拼接；SummaryMemory LLM 滚动摘要省 token；EntityMemory 按实体 KV；VectorStoreMemory 做相似检索。LangGraph 把 memory 抽象为可持久化 State channel，不只是 chat history，是任意结构化状态。**实际生产用 LangGraph Checkpointer**。

### RAG 系统设计（高频）

**Q6：百万级企业文档 RAG 召回链路怎么设计？为什么不能只上向量库？**（阿里云百炼/京东/腾讯 TI）
答：BM25(ES) + dense(HNSW/IVF_PQ) 混合 → **RRF 融合** → **Cross-encoder rerank**（bge-reranker-v2-m3 或 Qwen3-Reranker）→ top3~5；元数据预过滤（部门/时间/权限）缩小搜索空间；语义缓存命中直接返回。只上向量——查询和文档表达风格不对称时召回差，BM25 补长尾，rerank 去噪声。

**Q7：Chunking 怎么切才不破坏语义？**（字节飞书/百度）
答：固定窗口+overlap 是 baseline；优先按 Markdown 标题层级；Semantic Chunking（相邻句相似度突变切）；代码/表格单独处理；**Parent-Child**（小 chunk 检索 + 大 chunk 喂 LLM）最常用。

**Q8：Query 改写、HyDE、Step-back 各解决什么？**（美团/智谱）
答：改写处理口语化；HyDE 让 LLM 生成"伪答案文档"再向量检索解决 query-doc 表达不对称；Step-back 抽象出更泛化的问题再检索适合多跳；Multi-Query 生成 3~5 条改写并 RRF 合并。

**Q9：幻觉处理的工程手段？**（腾讯/MiniMax）
答：①检索端保召回（hit@k 评测）②prompt 强约束"仅基于上下文，缺失则不知道"③引用回标 + 后校验 NLI ④Self-RAG/CRAG 自反思是否再检索 ⑤RAGAs faithfulness 离线过滤。

**Q10：GraphRAG vs 传统 RAG vs Agentic RAG 场景？**（阿里达摩院/字节 Agent）
答：GraphRAG 多跳（人物关系/溯源）建图期 token 重；Agentic RAG 查询期迭代子问题（DeepSearcher/Search-R1）适合深度研究；传统 RAG 单跳 FAQ。

**Q11：长上下文（128K+）时代 RAG 还有价值吗？**（Kimi/通义）
答：有。①成本：128K prompt 单价高 ②精度："lost in middle" ③可控性：RAG 白盒可溯源可更新 ④权限隔离。长上下文 + RAG 常互补。

### Agent 架构（高频）

**Q12：ReAct vs Plan-and-Execute vs Reflexion**（字节/阿里云）
答：ReAct = Thought/Action/Observation 循环，灵活但易漂移；Plan-Execute planner 先出 DAG 再 executor，适合可预估、省 token；Reflexion 失败后 LLM 反思写 memory 再重试，代码/数学强。

**Q13：OpenAI Function Calling / MCP / A2A 关系？**（字节 TRAE/腾讯 IMA）
答：Function Calling 是模型层协议（返回结构化 JSON）；MCP 是 Client-Server 标准化工具/资源暴露协议；A2A 是 Agent 间互操作协议。**FC 管"怎么调"，MCP 管"工具怎么注册"，A2A 管"Agent 间怎么对话"**。

**Q14：多 Agent 相比单 Agent 的优势和坑？**（智谱/Datawhale）
答：优势——专业化分工、上下文解耦、可并行；坑——通信开销、错误传播、难调试、token 爆炸、循环调用、角色边界模糊。常用 Supervisor/Router + Worker（`create_supervisor`）。

**Q15：Tool 设计原则？LLM 调错工具怎么办？**（美团/kamacoder）
答：名字+description 清晰（**LLM 看的是 description**）；参数 JSON Schema 严格校验；返回截断防 token 爆炸；未知工具报错禁止"猜测执行"；幂等；危险操作加 HITL `interrupt()`。

**Q16：Agent 记忆怎么分层？上下文满了怎么办？**（字节/百度）
答：三层——短期（窗口）、中期（session/checkpoint）、长期（向量 + KV，Mem0/Zep）。溢出——滑窗、summary 压缩、重要性过滤归档、工具结果截断。

**Q17：HITL 在 LangGraph 怎么实现？**（阿里云百炼）
答：`interrupt()` 暂停 → 外部取 state → 人审核 → `Command(resume=value)` 继续；配 checkpoint 跨进程跨会话恢复。

### Prompt Engineering

**Q18：Self-Consistency 与 Tree of Thoughts 差别？**（字节）
答：SC 单路径多次采样后 majority vote；ToT 显式维护思维树、可回溯、BFS/DFS，成本高但 24 点/创意写作更好。

**Q19：Prompt 注入类型与防御？**（阿里安全/美团）
答：直接注入（"忽略之前指令"）、间接注入（RAG 文档藏指令）、越狱。防御：①数据与指令分离（`<data>` 标签、角色隔离）②输入/输出分类器（Llama Guard）③敏感操作 HITL ④输出结构化校验 ⑤最小权限工具。

**Q20：CoT 失效场景？**（智谱/MiniMax）
答：小模型（<10B）CoT 反而降分；常识简单问题 CoT 增噪；R1/o1 已内化 CoT 外层再加冗余；对齐税导致拒答。

### LLM 基础八股（必背）

**Q21：MHA / MQA / GQA / MLA 区别？KV Cache 怎么减？**（字节/DeepSeek）
答：MHA 每 head 独立 K/V；MQA 所有 head 共享一套（KV cache ÷ h_head 但效果损失大）；GQA 分 g 组共享（LLaMA2-70B、LLaMA3、Qwen2）；**MLA (DeepSeek-V2/V3) 低秩压缩 KV 到 latent 再反投影**，兼顾压缩率和效果。

**Q22：KV Cache 为什么只缓存 K/V 不缓存 Q？**（字节推理实习）
答：decode 阶段 Q 退化为当前 step 向量且每步重新算；公式 `2 × L × b × n_kv_heads × head_dim × dtype × n_layers`；Qwen2.5-7B 128K 约 7GB。

**Q23：RLHF 三阶段 vs DPO 区别？**（通义/智谱/Kimi）
答：RLHF = SFT + RM + PPO；DPO 把 RM+PPO 合并为用偏好对的分类损失，推导自 Bradley-Terry，去掉 reward model 和采样。生产 DPO 稳定但偏好数据敏感；GRPO (DeepSeek-R1) 省去 critic。

**Q24：LoRA/QLoRA 原理，为什么 A 高斯 B 全零？**（MiniMax/智谱）
答：冻结 W，学 ΔW = BA（秩 r << d）；B 初始化 0 保证训练初 ΔW=0 不破坏原模型；QLoRA 把 base 量化到 NF4 再训 LoRA，24G 卡可微调 65B。

**Q25：Fine-tuning vs RAG 怎么选？**（美团/腾讯）
答：FT 适合风格/格式/领域行话/固定能力；RAG 适合知识频繁更新、要溯源、数据稀疏。常见 FT（语气）+ RAG（实时知识）组合。SFT 后通用能力退化要 replay。

**Q26：vLLM 的 PagedAttention？Continuous Batching 解决什么？**（字节推理/阶跃）
答：KV cache 按 page（block）管理类似 OS 分页，碎片化 <4%；Continuous Batching 每 decode step 动态拼批不等整 batch 结束，吞吐 2-4×。

**Q27：Decoder-only 为何主流？**（百度/腾讯）
答：Scaling law 下训练简单、zero-shot 强、ICL 涌现；Encoder-decoder 参数利用率低；causal mask 天然适合自回归。

**Q28：位置编码从绝对→RoPE→ALiBi 演进？**（Kimi 长文本）
答：绝对 PE 泛化差；RoPE 相对位置旋转外推略差；ALiBi 线性偏置无需训练即外推；YaRN/NTK-aware 扩展 RoPE 做长文本。

### 系统设计

**Q29：QPS 1000 的 LLM 问答服务**（字节飞书/腾讯混元）
答：前置语义缓存（GPTCache 命中 30%+）；vLLM 多副本 + TP；K8s HPA 按 GPU 利用率扩缩；优先级队列 + 超时熔断；SSE 首 token <1s；观测 TTFT/TPOT/吞吐；模型路由（简单 query 走小模型）。

**Q30：流式 SSE vs WebSocket？断线重连？**（阿里/美团）
答：问答单向推 SSE（HTTP 鉴权/CDN 友好）；多轮互动用 WS；断线用 `Last-Event-ID` + 服务端 checkpoint 续推；Nginx 要 `X-Accel-Buffering: no`。

**Q31：向量库选型 Milvus/Qdrant/pgvector/ES knn**（京东/快手）
答：Milvus 分布式/十亿级；Qdrant 单机性能佳、Rust、filter-first；pgvector < 千万 + 已有 PG + 混合 SQL；ES 8+ knn 适合已有 ES 栈；大规模考虑 IVF_PQ/DiskANN 降成本。

**Q32：多租户 LLM 网关限流与成本归属？**（阿里云/字节火山）
答：OneAPI/Higress 风格；token 计量（input/output 分桶）；令牌桶 + Redis；用户/app 配额；超限降级小模型；审计日志 prompt 脱敏。

### 评估

**Q33：RAGAs 核心指标？**（腾讯/阿里）
答：Faithfulness（答案基于上下文）、Answer Relevancy（相关性）、Context Precision（检索命中率）、Context Recall（证据召回）。LLM-as-judge 计算，注意 judge 偏见。

**Q34：LLM-as-Judge 偏见与缓解？**（智谱）
答：位置偏差（偏爱先出现）、长度偏差、自我偏好、格式偏差。缓解：随机顺序双向打分、多 judge 投票、CoT + 参考答案、校准到人工。

**Q35：减少幻觉的系统性措施？**（百度/Kimi）
答：训练端 RLHF/DPO 对齐；推理端降 temperature/top_p；检索端加强证据；解码端 constrained decoding、JSON mode；事后校验（NLI 判断答案是否 entailed）。

### 项目深挖（压轴，必问）

每次面试最后 20 分钟几乎一定会问：
1. **"你这个 RAG 项目线上真实效果怎么评估？有 badcase 分析吗？"**
2. **"准召到底多少？和纯 BM25 基线差多少？为什么敢上线？"**
3. **"最大的坑是什么？怎么解决的？"**（期待技术深度 + 取舍思考）
4. **"向量库为什么选 X 不选 Y？量级/QPS/延迟/成本对比数据？"**
5. **"为什么不用 LangChain 原生 AgentExecutor，要自己写 LangGraph？你解决了什么？"**
6. **"如果重做这个项目，你会怎么改？"**

**准备这些的唯一方法是你的项目真的做深了**。建议每个项目都记 dev log，踩坑都写下来。

### 日本公司面试特点

日本公司（Mercari、Rakuten、LINE Yahoo、Sakana AI）的 AI 岗面试重过程描述和团队协作，不只是算法题。**简历必须是日式的"職務経歴書"格式**——详细到项目/技术栈/团队规模/你的具体贡献。代码面试风格英语化（LeetCode 中等），LLM/Agent 题和国内高度重叠（因为都参考 OpenAI/Anthropic 官方资源）。Mercari 面试官会用英语问你对"Go Bold / All for One"文化的理解——价值观面试是日企特色。

---

## 四、作品集：5 个让简历会说话的项目

作品集的基本盘是**3 个项目**：一个 RAG 深度项目、一个 Agent 多角色项目、一个差异化项目。多于 3 个也行，但每个都要做深。

### 项目 1：MedVision-Agent —— 医疗多模态诊断 Agent（差异化王牌）
**场景**：上传内窥镜图 → Agent 调用你的 PolySeg 息肉分割服务 → Qwen2.5-VL 描述病灶 → RAG 检索临床指南（NCCN/中华医学会）→ 生成结构化诊断建议，医生 HIL 审批。
**技术栈**：LangGraph StateGraph + Supervisor、PolySeg/YOLOv8 封装为 `@tool`、Qwen2.5-VL、Milvus + Qwen3-Embedding-4B、bge-reranker-v2-m3、FastAPI + Next.js（fork agent-chat-ui）、LangSmith trace、PostgresSaver。
**难度**：★★★★☆
**亮点**：**CV 模型工具化**（你最独特的能力）、HIL 合规节点、跨模态状态管理。
**面试价值**：你能把一个 ICLR/MICCAI 级别的 DL 模型包成 Agent 工具——**这一句话直接跳过"只会调 API"的筛选层**。

### 项目 2：刹车片智能巡检助手（工业落地）
**场景**：产线图输入 → YOLOv8 OBB 检测 + 分割 + 分类 → 查工艺 SOP RAG + 历史缺陷案例 → NG 原因 + 处置建议 + MCP 自动派工单到 MES。
**技术栈**：LangGraph + YOLOv8 (TorchServe) + pgvector + DeepSeek-V3（国产化加分）+ MCP 连 MES、Streamlit UI。
**难度**：★★★☆☆
**亮点**：**国产模型栈 + MCP 接入业务系统 + 批量图像 LangGraph Send 并行处理**。
**面试价值**：工业 AI/ToB 方向加分；讲得出"检测模型 → LLM → 业务系统"完整链路 = 系统思维满分。

### 项目 3：医学影像报告 RAG（论文复现）
**场景**：索引 10K+ 放射科/病理报告 + 教材，医生问诊时检索相似病例 + 引用权威文献。
**技术栈**：**GraphRAG（实体 = 疾病/部位/征象）+ RAPTOR 层次摘要 + Self-RAG reflection**；BGE-M3 sparse+dense hybrid + Qwen3-Reranker；LangSmith + RAGAS 评测闭环（faithfulness/context_recall/precision）。
**难度**：★★★★☆
**亮点**：**一次复现 3 篇顶级论文 + 完整评测工程化**。
**面试价值**：高阶 RAG 岗（阿里云百炼、字节飞书知识库）直接匹配；你能背得出 GraphRAG 论文里社区摘要的参数和 token 成本曲线 = 技术深度拉满。

### 项目 4：多 Agent 学术研究助手（对标 Deep Research）
**场景**：输入研究主题 → Planner 拆解 → 并行 Researcher 子 Agent（ArXiv / Semantic Scholar / 知网 MCP）→ Critic 审查 → Writer 生成综述 + 引用。
**技术栈**：Fork `open-deep-research` + 中文源改造 + PDF 解析；LangGraph Supervisor + Subgraphs；DeepSeek-R1（reasoning）+ Qwen-Turbo（summary）；agent-chat-ui 前端。
**难度**：★★★☆☆
**亮点**：**直接对标 OpenAI Deep Research，可量化评测**（Deep Research Bench）；展示并发、错误恢复、token 预算管理。
**面试价值**：Agent 岗必考"多 Agent 怎么做"——你有实战答案。

### 项目 5：Code Agent Mini（对标 Claude Code）
**场景**：本地 codebase 问答、代码修改、跑测试、PR 建议。
**技术栈**：`deepagents` 包 + 自定义 tools（ripgrep、AST 解析、pytest）+ MCP filesystem server；Qwen3-Coder 或 DeepSeek-V3；LangGraph Studio 可视化。
**难度**：★★★★☆
**亮点**：planning + virtual FS + subagent spawning；Git tools；VS Code 插件。
**面试价值**：AI Infra/开发者工具方向（字节 TRAE、阿里通义灵码、腾讯 CodeBuddy）**直接对口**。

**优先级建议**：先做完项目 1（你最独特）+ 项目 4（最能展示 LangGraph 能力），再加项目 3 或 5。**三个高质量比五个半成品有用十倍**。

---

## 五、资源清单：少而精

### 官方与课程
**第一优先**：LangChain Academy（academy.langchain.com，免费）——Intro to LangGraph、LangSmith Evals、**Deep Agents with LangGraph**（2025 新）。**DeepLearning.AI 短课**（Harrison Chase 亲自出镜）：AI Agents in LangGraph、Functions Tools and Agents、**Agent Memory**（2026 新）。**Anthropic Building Effective AI Agents**（resources.anthropic.com，2024-12）—— Anthropic 官方定义"workflow vs agent"，**业界必读**。**官方 Deep Research Course**（github.com/langchain-ai/deep_research_from_scratch）—— 从零手搓多 Agent 系统。

### 必读论文（附 arXiv）
经典：Attention Is All You Need (1706.03762)、RAG-Lewis (2005.11401)、CoT (2201.11903)、Self-Consistency (2203.11171)、ReAct (2210.03629)、Toolformer (2302.04761)、Reflexion (2303.11366)。
2024-2025：Self-RAG (2310.11511)、CRAG (2401.15884)、GraphRAG (2404.16130)、RAPTOR (2401.18059)、LATS (2310.04406)、Generative Agents (2304.03442)、AutoGen (2308.08155)、Anthropic Building Effective Agents（非 arXiv）。每篇看 10 分钟摘要 + 30 分钟主图足够面试应用层讲清楚。

### 中文社区
B 站必关注：**李宏毅**（生成式 AI 理论最系统）、**Datawhale**（self-llm、llm-universe、handy-multi-agents 三大开源教程）、**程序员寒山**、**AI 超元域**。知乎专栏：李 rumor、OneFlow、回旋托马斯。公众号：机器之心、量子位、PaperWeekly、LangChainAI 中文社区。面经必扫：GitHub `datawhalechina/hello-agents`、`wdndev/llm_interview_note`、`AngleMAXIN/llm-application-interview`；**niumianoffer 530+ 题库**。

### 日文资源（匹配你学日语 + 日本就业目标）
**Zenn**：搜 `LangGraph`、`LangChain 1.0`、`PydanticAI`；关注 `@kun432`（详细实战）、`@umi_mori`（Agent 系列）。**Qiita** LangChain tag 约 1500 篇，关注 `@hiromitsu_iwasaki`（LangSmith 评测）、`@K_poke`（RAG 优化）。书籍：**『LangChain 完全入門』（田村悠，技術評論社）v0.3 增补版**。社区：`LLM 勉強会` Connpass、Anthropic Tokyo Meetup（2025 起定期）。**读日文技术博客是同时练技术和日语的神器**，一举两得。

### 必关注开源项目
Dify（100K+ stars，可视化 workflow + MCP 全家桶，拆解它的源码 = 平台思维速成）、RagFlow（DeepDoc 深度文档解析，复杂 PDF 学习范本）、FastGPT、QAnything、`langchain-ai/open-deep-research`（Deep Research Bench #6）、`agent-chat-ui`（你简历前端的模板）、`deepagents` + `deep-agents-ui`。

### 工具平台账号（今天就注册）
LangSmith（免费 tier 够用）、**DeepSeek Platform**（充 50 块够你学半年）、通义千问 API（新人赠送额度）、Qdrant Cloud（免费 1GB）、HuggingFace（下 Embedding 模型）、GitHub（你所有项目的家）。

---

## 六、把焦虑换成行动的结语

你现在的位置是：研一上、Python 扎实、CV 背景过硬、LangChain 零基础、每天 1-2 小时、2029 毕业。算笔账——按这份路线 14 周走完核心闭环，你手上会有 **2-3 个能深入讲 30 分钟的 Agent 项目 + 完整 LangChain/LangGraph 知识体系 + 真实面经储备 + 英文/日文双语资源能力**。这个配置去面字节 Coze、阿里百炼、美团大模型应用组，**你是合格偏上的候选人**；去面 Mercari、Rakuten 的 AI SWE 岗，**你因为有 LangGraph 生产级经验反而比本地候选人更稀缺**。

学历焦虑的反义词是**简历厚度**。你本科做 PolySeg 双分支网络能读懂 Swin Transformer 源码——这种硬功夫本身就在前 20%。现在把它嫁接到 Agent 赛道，你就从"又一个做 CV 的硕士"变成"能把 DL 模型工具化的 Agent 工程师"，一句话就能让简历脱颖而出。微软 MSRA、亚马逊、NVIDIA 中国 AI 岗确实卡得严，但**这个行业 HC 最多的公司本来就不是它们**。字节一个季度放 300+ 大模型岗的 HC 里，211 硕士的占比远超你想象。

最后一个认知升级：**Agent 工程师在 2026-2027 仍然是红利期，但"调包侠"式 Agent 工程师已经开始被淘汰**。2026 年的 JD 普遍要求"全栈 + 推理优化 + 生产级系统设计"。这份路线为什么要你学 MCP、Deep Agents、LangGraph Platform、LangSmith 评测、vLLM 原理——不是因为我想让你累，是因为**这些就是 2026 年招聘 JD 里的新基线**。走完这份路线，你不是普通的 LangChain 用户，你是懂底层、会架构、能评测、能部署的 Agent 工程师。

行动从今晚开始。Day 1 是注册 DeepSeek API + 写第一段 Python 调用代码。别看完这份报告就点收藏夹——去把那 5 美金充进 DeepSeek 账户，打开终端 `pip install openai`。六个月后回头看今晚，你会感谢自己动了手。

日本也在等你。我们东京见。頑張って！