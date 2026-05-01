# Day 21 复盘笔记 — Week 3 综合项目：智能研究助手

## 今天做了什么

把 Week 3 所有技术整合成一个完整系统：**智能研究助手**

```
用户请求
    ↓
check_approval（敏感词检测）
    ↙              ↘
敏感操作          普通任务
    ↓                ↓
HIL 人工确认    Supervisor
    ↓           ↙        ↘
research_node  research  writing
               _agent    _agent
    ↓
END
```

---

## 关键设计决策

### 不要过度设计
原计划把 Supervisor + Plan-and-Execute + Reflexion 全部嵌套，但实际上：

```
嵌套太深 → 状态管理复杂 → 调试困难 → 维护成本高
```

**真实生产做法：按需组合，不过度设计。**

今天选择的组合：Supervisor + 专家Agent + HIL，已经覆盖了最核心的需求。

### HIL 放在最外层
```
check → HIL → Supervisor（内层）
```

不是放在 Supervisor 内部，而是在最外层做安全检查。原因：
- 统一的安全门，不管哪个 Agent 都要过
- Supervisor 内部逻辑不用关心安全问题
- 职责分离，好维护

---

## Week 3 完整回顾

| 天 | 核心内容 | 关键技术 |
|----|--------|---------|
| Day 15 | 复杂State+条件分支 | TypedDict多字段、Literal路由、回边 |
| Day 16 | Human-in-the-Loop | interrupt()、Command(resume)、PostgresSaver |
| Day 17 | 工具设计+MCP | description重要性、幂等、FastMCP |
| Day 18 | Plan-and-Execute | Planner+Executor循环+Reporter |
| Day 19 | Reflexion | Actor+Evaluator+Reflection，带教训重试 |
| Day 20 | Supervisor多Agent | create_supervisor、专家Agent分工 |
| Day 21 | 综合项目 | 按需组合，不过度设计 |

---

## 踩到的坑

### 坑1：HIL interrupt() 捕获方式
```python
# ❌ 错误：用 try/except 捕获
try:
    graph.invoke(...)
except Exception as e:
    pass  # LangGraph interrupt 不是普通异常

# ✅ 正确：用 get_state 检查图状态
result = graph.invoke(...)
snapshot = graph.get_state(config)
if snapshot.next == ("approval",):
    # 图暂停在 HIL 节点
    graph.invoke(Command(resume="确认"), config=config)
```

### 坑2：Supervisor 太聪明
Supervisor 会自主判断能不能做某件事，不会盲目执行危险操作（比如发邮件）。这是好事，但意味着 HIL 触发条件要更精准——用明确的操作词而不是意图词。

### 坑3：过度设计的诱惑
想把所有技术都用上，但嵌套太深反而让系统更脆弱。**简单、清晰、可维护**才是正确方向。

---

## 面试考点

**Q：多 Agent 系统怎么做安全控制？**  
答：在最外层加安全检查节点，检测敏感操作关键词，触发 HIL 等待人工确认。不在每个 Agent 内部各自做，统一安全门，职责分离，好维护。

**Q：生产环境多 Agent 系统的架构原则？**  
答：按需组合不过度设计；每个 Agent 职责单一；安全控制放最外层；接入 LangSmith 追踪；用持久化 checkpointer（PostgresSaver）支持 HIL；错误处理每层都要有。

**Q：Supervisor 和 HIL 怎么配合？**  
答：HIL 放在 Supervisor 外层做安全门，敏感操作先过 HIL 确认再进 Supervisor。这样 Supervisor 内部不用关心安全问题，职责分离清晰。

---

## 今日文件结构
```
week3/day21/
└── 01_research_assistant.py  ✅ Supervisor+专家Agent+HIL完整系统
```

---

## 下周预告 — Week 4：LangGraph 进阶 + 生产化
- Day 22：Subgraphs 子图
- Day 23：Send API 并行执行
- Day 24：长期记忆（Mem0）
- Day 25：LangSmith 追踪与评估
- Day 26：FastAPI 生产级部署
- Day 27：刹车片检测 Agent（你的项目！）
- Day 28：Week 4 收官