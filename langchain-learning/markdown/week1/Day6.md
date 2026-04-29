# Day 06 复盘笔记 — Memory 与对话管理

## 今天学了什么

### 1. 为什么需要记忆管理
- 100轮对话全部带上 → token 消耗爆炸
- 大部分模型有上下文长度限制（DeepSeek 64K）
- 需要策略性地管理历史消息

### 2. 三种记忆策略

| 策略 | 原理 | 优点 | 缺点 | 适合场景 |
|------|------|------|------|--------|
| 滑动窗口 | 只保留最近N条 | 简单 | 早期信息丢失 | 短对话、客服 |
| 摘要压缩 | LLM总结旧对话 | 保留要点 | 多一次LLM调用、有损失 | 中等对话 |
| 向量检索 | 存向量库按需检索 | 海量历史也能处理 | 实现复杂 | 长期记忆、跨会话 |

**生产环境常组合使用：**
```
短期：滑动窗口保留最近10轮
中期：摘要压缩保留本次会话要点
长期：Mem0/Zep 向量库跨会话用户画像
```

### 3. LangGraph State
```python
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

- `TypedDict`：定义状态的数据结构
- `Annotated[list, add_messages]`：messages 是列表，用 add_messages 合并而不是覆盖
- **为什么用合并不用覆盖：** 多个节点各自返回新消息，合并才能积累历史，覆盖会丢失之前的消息

### 4. MemorySaver + thread_id
```python
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# thread_id = 会话ID，同一个ID共享记忆
config = {"configurable": {"thread_id": "user_001"}}

graph.invoke(
    {"messages": [HumanMessage(content="你好")]},
    config=config,
)
```

- 同一个 `thread_id` → 共享记忆
- 不同 `thread_id` → 完全隔离，全新会话
- 多用户场景：每个用户一个 `thread_id`

### 5. 记忆积累的完整流程
```
第一轮：HumanMessage("我叫润实")
        ↓ add_messages 合并
State: [HumanMessage("我叫润实")]
        ↓ chat_node 执行
        ↓ add_messages 合并新回复
State: [HumanMessage("我叫润实"), AIMessage("你好润实！")]
        ↓ checkpointer 存储

第二轮：HumanMessage("我叫什么？")
        ↓ checkpointer 加载上一轮State
        ↓ add_messages 合并新消息
State: [HumanMessage("我叫润实"), AIMessage("你好润实！"), HumanMessage("我叫什么？")]
        ↓ 模型看到完整历史 → 记住了！
```

**记忆 = checkpointer 存状态 + add_messages 合并消息，缺一不可。**

### 6. 滑动窗口实现
```python
MAX_MESSAGES = 6

def chat_node(state: State):
    messages = state["messages"]
    
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]  # 只保留最后6条
    
    full_messages = [SystemMessage(content="...")] + messages
    response = model.invoke(full_messages)
    return {"messages": [response]}
```

`messages[-6:]` = Python切片，取列表最后6个元素。

### 7. 构建图的基本结构
```python
builder = StateGraph(State)          # 创建图
builder.add_node("chat", chat_node)  # 加节点
builder.add_edge(START, "chat")      # 连线：开始→chat
builder.add_edge("chat", END)        # 连线：chat→结束
graph = builder.compile(checkpointer=checkpointer)  # 编译
```

---

## 关键认知

> **thread_id 是会话隔离的基础。**
> 每个用户一个 thread_id，记忆完全隔离，这是多用户产品的核心设计。

> **滑动窗口简单但有代价。**
> 第1轮说"我叫润实"，第8轮就忘了——早期重要信息会丢失。

> **长期记忆需要向量库。**
> 跨会话的用户画像、历史记录，用 Mem0/Zep 存向量库，按需检索。

---

## 面试考点

**Q：LangGraph 的 add_messages 为什么用合并而不是覆盖？**  
答：多个节点并行执行时各自返回新消息，覆盖会导致只保留最后一个节点的消息，历史全部丢失。合并策略让每个节点只需返回增量，框架自动积累完整历史。

**Q：thread_id 有什么作用？**  
答：会话隔离的唯一标识。同一个 thread_id 共享完整记忆，不同 thread_id 完全隔离。多用户场景每个用户分配独立 thread_id，互不干扰。

**Q：三种记忆策略的区别和适用场景？**  
答：滑动窗口只保留最近N条，简单但丢失早期信息，适合短对话客服；摘要压缩用LLM总结旧对话，保留要点但有信息损失，适合中等长度对话；向量检索把历史存向量库按需检索，适合长期记忆和跨会话场景。生产环境常三种组合使用。

**Q：MemorySaver 和 PostgresSaver 的区别？**  
答：MemorySaver 把状态存在内存里，进程重启数据丢失，只适合测试。PostgresSaver 持久化到数据库，支持多进程、服务重启后恢复，是生产环境的选择。

---

## 今日文件结构
```
day06/
├── 01_memory_chat.py      ✅ LangGraph基础、MemorySaver、thread_id
└── 02_sliding_window.py   ✅ 滑动窗口、MAX_MESSAGES截断
```

---

## 明天预告 — Day 07：Week 1 综合项目
- 把 Day 1-6 所有知识串起来
- 做一个完整的"多功能命令行助手"
- 支持：流式输出、工具调用、结构化输出、多轮记忆
- 代码上传 GitHub，第一个完整项目！