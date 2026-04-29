# Day 07 复盘笔记 — Week 1 综合项目

## 今天做了什么

把 Day 1-6 所有知识串成一个完整项目：**带记忆的多工具命令行助手**

功能清单：
```
✓ 流式输出回复        （Day 2）
✓ 工具调用：查天气    （Day 3）
✓ 工具调用：数学计算  （Day 3）
✓ @tool 装饰器        （Day 3 升级版）
✓ LangGraph 多轮记忆  （Day 6）
✓ 命令行交互循环      （新加）
```

---

## 关键代码解析

### 1. @tool 装饰器
```python
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""  # docstring 自动变成 description
    ...
```
比 Day 3 手写 JSON Schema 简洁得多，函数名、参数类型、docstring 自动转成工具定义。

### 2. bind_tools
```python
model_with_tools = model.bind_tools(tools)
```
把工具列表绑定到模型，相当于 Day 3 里手写的 `tools=tools` 参数。

### 3. ToolNode
```python
tool_node = ToolNode(tools)
```
自动执行所有 tool_calls，替代了 Day 3 手写的工具执行循环：
```python
# Day 3 手写（不用再写了）：
for tool_call in message.tool_calls:
    func_name = tool_call.function.name
    result = available_tools[func_name](**func_args)
```

### 4. 条件路由
```python
def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"   # 有工具调用 → 去工具节点
    return END           # 没有 → 结束

builder.add_conditional_edges("model", should_continue)
```
替代了 Day 3 里的 `finish_reason` 判断。

**add_edge vs add_conditional_edges：**
```python
add_edge("A", "B")               # 固定：A执行完永远去B
add_conditional_edges("A", func) # 动态：根据func返回值决定去哪
```

### 5. 完整图结构
```
START → model → should_continue → tools → model → ...
                      ↓
                     END
```

```python
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue)
builder.add_edge("tools", "model")  # 工具执行完回到模型
```

### 6. 流式输出 + 节点过滤
```python
for chunk, metadata in graph.stream(
    {"messages": [HumanMessage(content=user_input)]},
    config=config,
    stream_mode="messages",
):
    if hasattr(chunk, "content") and chunk.content:
        if metadata.get("langgraph_node") == "model":  # 只打印模型节点输出
            print(chunk.content, end="", flush=True)
```
图里有多个节点，用 `langgraph_node` 过滤，只打印来自 model 节点的流式回复。

### 7. 记忆（和 Day 6 完全一样）
```python
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "assistant_001"}}
```
没有任何新东西，checkpointer + thread_id 自动管理记忆。

---

## Week 1 知识回顾

| 天 | 核心内容 | 关键代码 |
|----|--------|--------|
| Day 1 | LLM API、messages结构、无记忆 | `client.chat.completions.create()` |
| Day 2 | 流式输出、SSE、FastAPI | `stream=True`、`yield`、`StreamingResponse` |
| Day 3 | Function Calling、Agent循环 | `tool_calls`、`while True`、`available_tools` |
| Day 4 | LangChain核心、LCEL管道 | `init_chat_model`、`prompt | model | parser` |
| Day 5 | 结构化输出、Pydantic | `with_structured_output(Schema)` |
| Day 6 | LangGraph记忆管理 | `MemorySaver`、`thread_id`、`add_messages` |
| Day 7 | 综合项目 | `@tool`、`ToolNode`、`add_conditional_edges` |

---

## 面试考点

**Q：LangGraph 里 add_edge 和 add_conditional_edges 的区别？**  
答：add_edge 是固定路由，A执行完永远去B；add_conditional_edges 是动态路由，根据路由函数的返回值决定下一步去哪个节点，适合需要判断的场景（比如有没有工具调用）。

**Q：ToolNode 解决了什么问题？**  
答：封装了工具执行的完整流程——解析 tool_calls、找到对应函数、执行、把结果包装成 ToolMessage 塞回 messages。不用再手写循环，一行代码搞定。

**Q：为什么工具节点执行完要回到模型节点？**  
答：工具只是执行动作返回结果，模型需要拿到工具结果后再理解、整理、用自然语言回复用户。工具→模型→回复是完整闭环。

**Q：stream_mode="messages" 是什么？**  
答：LangGraph 的流式模式，按消息块返回，每个 chunk 是一小段文字。配合 metadata 里的 langgraph_node 可以过滤只显示特定节点的输出。

---

## 今日文件结构
```
day07/
└── assistant.py  ✅ 完整多工具记忆助手
```

---

## 下周预告 — Week 2：RAG 系统
- Day 08：文档加载（PDF、网页、Word）
- Day 09：文本切分策略
- Day 10：Embedding 与向量数据库
- Day 11：基础 RAG 系统搭建
- Day 12：召回优化（混合检索、Reranker）
- Day 13：高阶 RAG（HyDE、多查询、Self-RAG）
- Day 14：RAG 评估（RAGAs）