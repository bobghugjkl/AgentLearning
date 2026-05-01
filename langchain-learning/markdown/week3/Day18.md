# Day 18 复盘笔记 — Plan-and-Execute Agent

## 今天学了什么

### 1. ReAct vs Plan-and-Execute

| | ReAct | Plan-and-Execute |
|--|-------|-----------------|
| 工作方式 | 想一步做一步 | 先规划所有步骤再执行 |
| 适合场景 | 任务随时可能变化 | 步骤可预估的复杂任务 |
| Token消耗 | 多（每步都要思考） | 少（规划一次，执行更直接） |
| 并行能力 | 弱 | 强（独立步骤可并行） |
| 灵活性 | 高 | 低（计划制定后难调整） |

**一句话记住：**
```
任务步骤可预估 → Plan-and-Execute
任务随时可能变化 → ReAct
简单问题 → ReAct（Plan-and-Execute 反而多余）
```

### 2. State 设计

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    plan: List[str]        # 规划的步骤列表
    current_step: int      # 当前执行到第几步（循环计数器）
    results: List[str]     # 每步的执行结果
    final_report: str      # 最终报告
```

### 3. 三个节点

**Planner（规划）：**
```python
def planner_node(state: State):
    task = state["messages"][-1].content
    # 让模型把任务分解成3-5步
    response = model.invoke(planner_prompt)
    steps = response.content.strip().split("\n")
    
    return {
        "plan": steps,
        "current_step": 0,  # 从第0步开始
        "results": [],
    }
```

**Executor（执行，循环）：**
```python
def executor_node(state: State):
    current = state["current_step"]
    step = state["plan"][current]
    
    # 让模型选工具执行这步
    model_with_tools = model.bind_tools(tools)
    response = model_with_tools.invoke(step)
    
    # 执行工具
    result = tool_func.invoke(tc["args"])
    
    return {
        "current_step": current + 1,          # 步骤+1
        "results": state["results"] + [result], # 追加结果
    }
```

**Reporter（汇总）：**
```python
def reporter_node(state: State):
    results_text = "\n".join(state["results"])
    # 让模型根据所有步骤结果生成报告
    response = model.invoke(report_prompt)
    return {"final_report": response.content}
```

### 4. 路由函数 + 回边（循环核心）

```python
def should_continue(state: State) -> str:
    if state["current_step"] >= len(state["plan"]):
        return "report"   # 步骤全完成 → 生成报告
    return "execute"      # 还有步骤 → 继续执行

builder.add_conditional_edges(
    "executor",
    should_continue,
    {
        "execute": "executor",  # ← 回边！循环
        "report": "reporter",
    }
)
```

**执行流程：**
```
planner（生成N步计划）
    ↓
executor（执行第1步，current 0→1）
    ↓ 还有步骤
executor（执行第2步，current 1→2）
    ↓ 还有步骤
executor（执行第N步，current N-1→N）
    ↓ 步骤全完成
reporter（汇总生成报告）
    ↓
END
```

### 5. 完整图结构

```python
builder.add_edge(START, "planner")
builder.add_edge("planner", "executor")
builder.add_conditional_edges("executor", should_continue, {
    "execute": "executor",  # 回边
    "report": "reporter",
})
builder.add_edge("reporter", END)
```

### 6. Plan-and-Execute 的缺点

**缺点1：步骤串行**
独立步骤也要一个一个来，不能并行。
解决：LangGraph 的 Send API（并行 map-reduce）

**缺点2：计划固定，无法调整**
Planner 一次性规划，执行中途无法根据实际结果修正。
解决：加 Replanner 节点，执行几步后重新规划

**缺点3：工具调用次数不可控**
Executor 没有限制，模型可能每步调多次工具。
解决：在 executor_prompt 里明确限制"每步只调用一次工具"

---

## 面试考点

**Q：Plan-and-Execute 和 ReAct 的区别？**  
答：ReAct 想一步做一步，灵活但可能绕弯路；Plan-and-Execute 先规划所有步骤再执行，适合步骤可预估的复杂任务，token消耗更可控，步骤清晰便于调试。

**Q：Plan-and-Execute 什么时候不适合用？**  
答：简单问题（一步就能回答）或任务随时可能变化的场景。简单问题用 Plan-and-Execute 反而增加了不必要的规划开销；任务变化快的场景规划可能很快过时。

**Q：Plan-and-Execute 的循环怎么实现？**  
答：用 `current_step` 作为计数器，每次执行后+1。路由函数判断 `current_step >= len(plan)` 时跳出循环去报告节点，否则回到 executor 继续执行（回边）。

**Q：Plan-and-Execute 的缺点和改进方向？**  
答：步骤串行慢（用Send API并行）、计划固定无法调整（加Replanner）、工具调用次数不可控（prompt限制）。

---

## 今日文件结构
```
week3/day18/
└── 01_plan_execute.py  ✅ Planner+Executor循环+Reporter，完整Plan-and-Execute
```

---

## 明天预告 — Day 19：Reflexion 自反思
- Agent 失败后怎么自动反思和改进
- Reflexion 论文的核心思想
- 实现一个失败后自动重试并改进的 Agent
- 什么时候用 Reflexion？