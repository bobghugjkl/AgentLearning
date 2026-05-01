# Day 15 复盘笔记 — LangGraph 复杂状态与条件分支

## 今天学了什么

### 1. 复杂 State（多字段）

```python
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]  # 对话历史（合并）
    task_type: str        # 任务类型：general/code/math
    risk_level: str       # 风险级别：low/high
    retry_count: int      # 重试次数
```

**关键点：**
- 每个节点只返回自己要更新的字段，其他字段不变
- `messages` 用 `add_messages` 合并，其他字段直接覆盖

```python
def classify_node(state: State):
    # 只更新这三个字段，messages 不动
    return {
        "task_type": "code",
        "risk_level": "low",
        "retry_count": 0,
    }
```

### 2. 条件分支完整写法

```python
from typing import Literal

# 路由函数：返回值对应节点名
def route_by_type(state: State) -> Literal["general", "code", "high_risk"]:
    if state["risk_level"] == "high":
        return "high_risk"
    if state["task_type"] == "code":
        return "code"
    return "general"

# 条件边：把路由函数的返回值映射到节点
builder.add_conditional_edges(
    "classify",          # 从哪个节点出发
    route_by_type,       # 路由函数
    {
        "general": "general",      # 返回"general"→去general节点
        "code": "code",
        "high_risk": "high_risk",
    }
)
```

### 3. 图的完整结构

```
START
  ↓
classify（分析任务类型和风险）
  ↓
route_by_type（条件判断）
  ↙        ↓        ↘
general   code   high_risk
  ↘        ↓        ↙
          END
```

```python
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_by_type, {...})
builder.add_edge("general", END)
builder.add_edge("code", END)
builder.add_edge("high_risk", END)
```

### 4. 回边（循环）实现重试

```python
def should_retry(state: State) -> Literal["retry", "end"]:
    last_msg = state["messages"][-1].content
    if "错误" in last_msg and state["retry_count"] < 3:
        return "retry"
    return "end"

# 回边：code节点失败时回到自己
builder.add_conditional_edges("code", should_retry, {
    "retry": "code",  # ← 回边，形成循环
    "end": END,
})
```

**这是 LangGraph 比 LangChain Chain 强大的核心：支持循环！**

### 5. 固定边 vs 条件边

```python
# 固定边：A执行完永远去B
builder.add_edge("A", "B")

# 条件边：A执行完根据函数决定去哪
builder.add_conditional_edges("A", routing_fn, {"result1": "B", "result2": "C"})
```

### 6. 今天的图结构（三分支）

```python
# 测试结果：
# 普通问题 → general + low  → 普通节点 → 正常回答
# 代码问题 → code + low     → 代码节点 → 专业代码
# 危险操作 → code + high    → 高风险节点 → 拒绝执行
```

---

## 面试考点

**Q：LangGraph 和 LangChain Chain 的核心区别？**  
答：LangChain Chain 是有向无环图（DAG），只能顺序执行，不支持循环。LangGraph 是状态图，支持分支、循环、回边，可以实现 Agent 的工具调用循环、重试机制、复杂条件分支等。

**Q：State 里的字段为什么有的用 Annotated，有的不用？**  
答：`Annotated[list, add_messages]` 指定了 Reducer——多个节点并行写入时用 `add_messages` 合并而不是覆盖。普通字段（str、int、bool）直接覆盖，不需要 Reducer。

**Q：条件边的路由函数返回值类型为什么要用 Literal？**  
答：`Literal["general", "code", "high_risk"]` 限制返回值只能是这几个字符串，Python 类型检查可以提前发现错误，也让代码意图更清晰。

**Q：retry_count 字段有什么用？**  
答：防止无限循环。每次重试 +1，超过最大次数（比如3次）就强制结束，避免 Agent 陷入死循环消耗大量 token 和时间。

**Q：节点函数只返回部分字段，其他字段会消失吗？**  
答：不会。LangGraph 会把节点返回的字段合并到现有 State 上，没有返回的字段保持原值不变。

---

## 今日文件结构
```
week3/day15/
└── 01_complex_state.py  ✅ 多字段State、条件分支、三路由、回边原理
```

---

## 明天预告 — Day 16：Human-in-the-Loop
- 什么是 HIL，为什么生产环境必须有人工审批
- `interrupt()` 暂停图的执行
- `Command(resume=value)` 继续执行
- 实现一个"危险操作需要人工确认"的 Agent