# Day 25 复盘笔记 — LangSmith 追踪与评估

## 今天学了什么

### 1. 为什么需要可观测性

没有 LangSmith 时排查问题：
```
用户：回答慢
你：慢在哪步？不知道，没有记录

用户：回答错了
你：是检索错了还是LLM错了？不知道，看不到中间过程
```

有了 LangSmith：
```
直接看 trace → 每步输入输出、耗时、token消耗一目了然
```

### 2. 零代码接入（最重要！）

只需在 `.env` 里加两个变量，**不用改任何代码**：

```bash
LANGSMITH_API_KEY=你的key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=langchain-learning  # 项目名，可选
```

之后所有 `model.invoke()`、`graph.invoke()`、`chain.invoke()` 自动上传到 LangSmith。

### 3. Trace 里能看到什么

```
LangGraph（2.60s，891 tokens）
├── agent（第一轮）
│   ├── call_model → ChatDeepSeek（408 tokens）
│   ├── should_continue
│   └── tools
│       ├── get_weather（city=北京）
│       └── calculate（123*456）
└── agent（第二轮）
    └── call_model → ChatDeepSeek（483 tokens）
```

**关键指标：**
- `Latency`：每步耗时，找性能瓶颈
- `Tokens`：消耗统计，控制成本
- `Error`：有没有报错
- `Input/Output`：每步的输入输出

### 4. 为什么第二次 call_model 比第一次 token 多

```
第一次：messages = [用户问题] → 408 tokens
第二次：messages = [用户问题 + 工具调用 + 工具结果] → 483 tokens
```

每轮都带完整历史，所以越来越多。

### 5. @traceable 追踪自定义函数

```python
from langsmith import traceable

@traceable(name="RAG Pipeline")  # 自定义 trace 名字
def my_rag(question: str) -> str:
    context = f"检索到的内容..."
    response = model.invoke(f"根据以下内容回答：{context}\n\n{question}")
    return response.content
```

任何 Python 函数加 `@traceable` 就会出现在 LangSmith trace 里，不只是 LangChain 组件。

### 6. LangSmith 的使用场景

**开发阶段：**
- 查看每步输入输出，调试 prompt
- 对比不同 prompt 版本的效果

**生产阶段：**
- 监控 token 消耗和成本
- 排查慢请求和错误
- 追踪用户反馈对应的具体调用

**评估阶段：**
- 创建 Dataset（测试集）
- 批量运行评估
- 对比不同版本的质量

---

## 面试考点

**Q：你们的 Agent 上线后怎么监控？**  
答：用 LangSmith 追踪，只需设置两个环境变量就能自动记录所有 LLM 调用。可以看到每步的输入输出、延迟、token消耗，出问题直接查 trace，不需要改代码加日志。

**Q：LangSmith 怎么追踪自定义函数？**  
答：用 `@traceable` 装饰器，函数就会出现在 LangSmith 的 trace 树里，可以看到输入输出和耗时。适合追踪 RAG 的检索步骤、数据处理等自定义逻辑。

**Q：Agent 运行时 token 为什么越来越多？**  
答：每次 LLM 调用都会把完整的 messages 历史带上，包括用户问题、工具调用记录、工具结果。随着对话轮数增加，context 越来越长，token 消耗成倍增长。这就是为什么需要记忆压缩和滑动窗口。

**Q：如何用 LangSmith 做 prompt 版本管理？**  
答：LangSmith 的 Prompt Hub 可以存储不同版本的 prompt，每次修改会记录版本历史。配合 Dataset 评估，可以对比新旧 prompt 在测试集上的性能，防止 prompt 改坏了。

---

## 今日文件结构
```
week4/day25/
└── 01_langsmith_trace.py  ✅ 自动追踪、Agent trace、@traceable自定义函数
```

---

## 明天预告 — Day 26：刹车片检测 Agent
- 把你的 YOLOv8 刹车片检测系统包装成 Agent 工具
- 结合 RAG（查 SOP 文档）
- 生成检测报告 + 处置建议
- 你最有差异化竞争力的项目！