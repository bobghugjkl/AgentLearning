# Day 20 复盘笔记 — 多 Agent Supervisor 模式

## 今天学了什么

### 1. 为什么需要多 Agent

```
单个 Agent 做所有事：
- 工具太多，模型容易选错
- prompt 太长，性能下降
- 一个功能出问题，整个 Agent 崩

多 Agent 分工：
- 每个 Agent 只做一件事，更专业
- 工具少，模型选择更准确
- 独立维护，互不影响
- 可以并行执行
```

### 2. Supervisor 模式架构

```
用户请求
    ↓
Supervisor（LLM判断派给谁）
    ↙        ↓        ↘
代码Agent  写作Agent  数学Agent
    ↘        ↓        ↙
Supervisor（汇总结果）
    ↓
返回给用户
```

**Supervisor 职责：**
- ✅ 判断派给哪个专家
- ✅ 汇总专家的结果
- ✅ 必要时补充说明
- ❌ 不应该替代专家做专业工作

### 3. 代码实现

```python
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

# 创建专家 Agent
code_agent = create_react_agent(
    model,
    tools=[run_python, explain_code],
    name="code_agent",
    prompt="你是一个专业的Python程序员。",
)

writing_agent = create_react_agent(
    model,
    tools=[check_grammar, improve_style],
    name="writing_agent",
    prompt="你是一个专业的写作助手。",
)

math_agent = create_react_agent(
    model,
    tools=[calculate, solve_equation],
    name="math_agent",
    prompt="你是一个数学专家。",
)

# 创建 Supervisor
supervisor = create_supervisor(
    agents=[code_agent, writing_agent, math_agent],
    model=model,
    prompt="""你是任务分配专家：
- code_agent：代码相关问题
- writing_agent：写作语法相关
- math_agent：数学计算相关""",
).compile()
```

### 4. Supervisor vs 条件边路由

| | 条件边路由（Day 15） | Supervisor 模式 |
|--|-------------------|----------------|
| 判断方式 | 代码写死的规则 | LLM 理解语义 |
| 灵活性 | 低（只能处理预定义情况） | 高（能处理复杂意图） |
| 维护成本 | 低 | 高 |
| 适合场景 | 规则明确的分支 | 意图复杂的任务分发 |

### 5. 多 Agent 的四个坑

**坑1：Agent 间不能直接通信**
```
必须通过 Supervisor 中转 → 复杂任务效率低
解决：用 Swarm 模式（Agent 间直接 handoff）
```

**坑2：错误传播**
```
一个 Agent 出错 → 错误结果传给下游 → 全错
解决：每个 Agent 加错误处理和验证
```

**坑3：token 爆炸**
```
每个 Agent 都有 messages 历史
多 Agent 来回通信 → token 消耗成倍增加
解决：限制 message 历史长度
```

**坑4：调试困难**
```
出问题不知道是哪个 Agent 的锅
解决：接入 LangSmith 追踪每个 Agent 行为
```

### 6. Supervisor vs Swarm 对比

| | Supervisor 模式 | Swarm 模式 |
|--|----------------|-----------|
| 协调方式 | 中央 Supervisor 统一调度 | Agent 间直接 handoff |
| 适合场景 | 任务分工明确 | 任务需要多 Agent 协作 |
| 实现复杂度 | 低 | 中 |
| 灵活性 | 中 | 高 |

---

## 面试考点

**Q：为什么要用多 Agent 而不是单 Agent？**  
答：单 Agent 工具太多时模型容易选错，prompt 太长性能下降，一个功能出问题整个崩。多 Agent 每个专注一件事，工具少选择更准，独立维护互不影响，还可以并行执行。

**Q：Supervisor 模式的工作原理？**  
答：用户请求发给 Supervisor（一个 LLM），Supervisor 理解意图后决定派给哪个专家 Agent，专家完成任务后把结果返回给 Supervisor，Supervisor 汇总后返回给用户。

**Q：多 Agent 系统有哪些常见问题？**  
答：Agent 间不能直接通信（必须通过 Supervisor 中转）、错误传播（一个 Agent 出错影响全局）、token 爆炸（多 Agent 历史累积）、调试困难（不知道哪个 Agent 出问题）。解决方案：Swarm 模式、错误处理、历史限制、LangSmith 追踪。

**Q：Supervisor 模式和条件边路由有什么区别？**  
答：条件边路由是代码写死的规则（if-else），只能处理预定义情况，维护成本低；Supervisor 用 LLM 理解语义，能处理复杂意图，更灵活但维护成本高。规则明确用条件边，意图复杂用 Supervisor。

---

## 今日文件结构
```
week3/day20/
└── 01_supervisor.py  ✅ 三专家Agent+Supervisor路由，多Agent坑分析
```

---

## 明天预告 — Day 21：Week 3 综合项目
- 把 Week 3 所有技术整合
- 多 Agent 研究助手：Supervisor + 专家 Agent + HIL + Reflexion
- 支持：任务规划、专家分工、人工审批、自动反思
- 代码上传 GitHub，第三个完整项目！