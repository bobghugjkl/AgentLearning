# Day 22 复盘笔记 — Subgraphs 子图

## 今天学了什么

### 1. 为什么需要子图

当 Agent 内部逻辑复杂时，不要把所有步骤塞进一个节点——用子图封装：

```
主图（简洁）
├── router 节点
├── general 节点
└── research 节点 ← 这里是子图！
        ↓
    子图（复杂逻辑封装在内部）
    ├── search 节点
    ├── analyze 节点
    └── summarize 节点
```

**子图的好处：**
- 复杂逻辑封装，主图保持简洁
- 子图可以独立测试
- 子图可以复用（多个主图共享）
- 调试时可以单独跑子图

### 2. State 的继承关系

```python
# 主图 State
class MainState(TypedDict):
    messages: Annotated[list, add_messages]  # 共享字段
    task_type: str

# 子图 State
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]  # 共享字段（同名自动传递）
    search_result: str    # 子图私有，主图看不到
    analysis_result: str  # 子图私有
    final_result: str     # 子图私有
```

**规则：同名字段自动传递，子图私有字段主图看不到。**

### 3. 子图的构建和使用

```python
# 1. 构建子图
sub_builder = StateGraph(ResearchState)
sub_builder.add_node("search", search_node)
sub_builder.add_node("analyze", analyze_node)
sub_builder.add_node("summarize", summarize_node)
sub_builder.add_edge(START, "search")
sub_builder.add_edge("search", "analyze")
sub_builder.add_edge("analyze", "summarize")
sub_builder.add_edge("summarize", END)

# 编译子图（不需要 checkpointer）
research_subgraph = sub_builder.compile()

# 2. 把子图作为节点加入主图
main_builder.add_node("research", research_subgraph)  # ← 直接传编译后的图
```

### 4. 子图作为节点的原理

```python
# 普通节点：传函数
main_builder.add_node("general", general_node)
# LangGraph 调用：general_node(state)

# 子图节点：传编译后的图
main_builder.add_node("research", research_subgraph)
# LangGraph 调用：research_subgraph.invoke(state)
```

LangGraph 把子图的 `.invoke()` 当成节点函数调用，传入主图 State，执行完把共享字段合并回主图。

### 5. 完整主图结构

```python
main_builder = StateGraph(MainState)
main_builder.add_node("router", router_node)
main_builder.add_node("general", general_node)
main_builder.add_node("research", research_subgraph)  # 子图节点

main_builder.add_edge(START, "router")
main_builder.add_conditional_edges(
    "router",
    route_task,
    {
        "research": "research",  # → 子图
        "general": "general",
    }
)
main_builder.add_edge("research", END)
main_builder.add_edge("general", END)

graph = main_builder.compile(checkpointer=MemorySaver())
```

### 6. 类比理解

```
主图 = 公司流程
子图 = 某个部门的内部流程

主图说："去研究部门处理这个任务"
研究部门内部：搜索→分析→摘要（主图不关心细节）
处理完把结果交回主图

主图只知道"叫研究部门"，不关心内部怎么运作
```

---

## 面试考点

**Q：什么是 LangGraph 的子图？有什么用？**  
答：把复杂逻辑封装成独立的图，作为节点嵌入主图。好处是主图保持简洁、子图可独立测试和复用、复杂逻辑封装后便于维护。

**Q：子图和主图怎么传递数据？**  
答：通过共享字段——同名字段自动传递。主图 State 和子图 State 中字段名相同的会自动同步，子图私有字段主图看不到。

**Q：子图作为节点的原理是什么？**  
答：LangGraph 把编译后的子图对象的 `.invoke()` 方法当成节点函数调用，传入当前 State，执行完把共享字段合并回主图 State。

**Q：子图需要自己的 checkpointer 吗？**  
答：不需要。子图编译时不加 checkpointer，由主图的 checkpointer 统一管理整个执行过程的状态持久化。

---

## 今日文件结构
```
week4/day22/
└── 01_subgraph.py  ✅ 子图构建、主图嵌套、共享State、路由测试
```

---

## 明天预告 — Day 23：Send API 并行执行
- 为什么需要并行执行
- Send API：动态 spawn 多个并发节点
- Map-Reduce 模式在 LangGraph 里怎么实现
- 批量任务并行处理实战