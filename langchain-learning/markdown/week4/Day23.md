# Day 23 复盘笔记 — Send API 并行执行

## 今天学了什么

### 1. 为什么需要并行执行

```
串行（Plan-and-Execute）：
搜索主题1 → 搜索主题2 → 搜索主题3 → 汇总
耗时：3秒

并行（Send API）：
搜索主题1 ─┐
搜索主题2 ─┤→ 同时执行 → 汇总
搜索主题3 ─┘
耗时：1秒
```

**适合场景：** 多个独立子任务，互不依赖，可以同时跑（Map-Reduce 模式）。

### 2. 并行的风险：State 写入冲突

```python
# ❌ 普通字段：并行节点后写覆盖先写，数据丢失
result: str

# ✅ 用 Reducer：自动合并所有写入
results: Annotated[List[str], operator.add]
```

**并行场景必须用 Reducer 防止覆盖。**

### 3. Send API 核心用法

**关键：Send 必须在条件边函数里返回，不能在普通节点里！**

```python
# ✅ 正确：条件边函数返回 Send 列表
def dispatch_research(state: ResearchState):
    return [
        Send("research", {"topic": topic, "results": []})
        for topic in state["topics"]
    ]

builder.add_conditional_edges(
    "planner",
    dispatch_research,  # ← 条件边函数
)

# ❌ 错误：普通节点不能返回 Send 列表
def dispatch_node(state):
    return [Send(...)]  # 报错！节点必须返回字典
```

### 4. Send 的结构

```python
Send("research", {"topic": "技术原理", "results": []})
  ↑                ↑
  目标节点名        传给该节点的数据（子任务 State）
```

LangGraph 看到 Send 列表，同时启动多个目标节点实例：

```
Send → research_node（topic="技术原理"）─┐
Send → research_node（topic="应用场景"）─┤ 同时执行！
Send → research_node（topic="发展趋势"）─┘
```

### 5. 两个 State 的分工

```python
# 主图 State（全局）
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    topics: List[str]                           # 主题列表
    results: Annotated[List[str], operator.add] # 并行结果合并
    final_report: str

# 子任务 State（每个并行实例独立）
class TopicState(TypedDict):
    topic: str      # 当前实例的主题
    results: Annotated[List[str], operator.add]  # 写回主图
```

### 6. 完整 Map-Reduce 图结构

```python
builder.add_edge(START, "planner")

# Map 阶段：条件边触发并行
builder.add_conditional_edges("planner", dispatch_research)

# 所有并行节点完成后自动汇聚
builder.add_edge("research", "reduce")
builder.add_edge("reduce", END)
```

流程：
```
START
  ↓
planner（拆任务，生成 topics 列表）
  ↓ 条件边（dispatch_research）
research × N（并行执行，operator.add 合并结果）
  ↓ 全部完成后汇聚
reduce（汇总生成报告）
  ↓
END
```

### 7. 条件边的两种返回值

```python
# 返回字符串 → 决定走哪条边（Day 15）
def route(state) -> str:
    return "node_a" or "node_b"

# 返回 Send 列表 → 触发并行（今天）
def dispatch(state) -> list:
    return [Send("node", data) for data in items]
```

---

## 踩坑记录

**错误：** 把 Send API 放在普通节点里返回

```
langgraph.errors.InvalidUpdateError: 
Expected dict, got [Send(...), Send(...)]
```

**原因：** 普通节点必须返回字典，Send 列表只能在条件边函数里返回。

**解决：** 把 dispatch 从节点改为条件边函数，用 `add_conditional_edges` 注册。

---

## 面试考点

**Q：LangGraph 的 Send API 是什么？有什么用？**  
答：在条件边函数里返回 Send 列表，LangGraph 会同时启动多个目标节点实例并行执行。适合 Map-Reduce 模式——把任务拆成独立子任务并行处理，最后汇总结果。

**Q：并行节点同时写入 State 怎么处理冲突？**  
答：用 Reducer。普通字段后写覆盖先写会丢数据，用 `Annotated[List[str], operator.add]` 定义的字段会把所有并行节点的写入追加合并，不会覆盖。

**Q：Send API 为什么必须在条件边里？**  
答：LangGraph 规定普通节点必须返回字典（State 的更新），Send 列表是图结构的控制信号，不是 State 更新，所以只能在条件边函数里返回。

**Q：Map-Reduce 在 LangGraph 里怎么实现？**  
答：Map 阶段用条件边函数返回 Send 列表触发并行；并行节点用 operator.add 的 Reducer 把结果追加到共享列表；所有并行节点完成后自动汇聚到下一个节点（Reduce 阶段）做汇总。

---

## 今日文件结构
```
week4/day23/
└── 01_send_api.py  ✅ Send API并行、operator.add防覆盖、Map-Reduce
```

---

## 明天预告 — Day 24：长期记忆（Mem0）
- MemorySaver 只能记住当前会话，跨会话怎么办？
- Mem0：专门做长期记忆的库
- 用户画像、历史偏好跨会话持久化
- 实现一个"记住你是谁"的 Agent