# Day 16 复盘笔记 — Human-in-the-Loop（HIL）

## 今天学了什么

### 1. 为什么需要 HIL
AI Agent 可能误解用户意图，直接执行危险操作（误删文件、误发邮件、误转账）。
HIL 在危险操作前强制暂停，等待人工确认，是生产环境 Agent 最重要的安全机制。

### 2. HIL 工作原理

```
图执行到 interrupt()
    ↓
把当前 State 存到 checkpointer
    ↓
返回给调用方（携带 interrupt 的内容）
    ↓
调用方等待用户输入...（图不在运行）
    ↓
用户输入确认
    ↓
Command(resume=value) 传入
    ↓
从 checkpointer 恢复 State，继续执行
```

**关键：checkpointer 是 HIL 的基础，没有它就无法恢复执行。**

### 3. interrupt() 用法

```python
from langgraph.types import interrupt, Command

def human_approval(state: State):
    # 暂停！把需要确认的信息发给用户
    user_decision = interrupt({
        "message": f"⚠️ 高风险操作：'{last_msg}'\n确认执行？",
        "options": ["确认执行", "取消"],
    })
    
    # 用户回复后从这里继续
    approved = user_decision == "确认执行"
    return {"approved": approved}
```

### 4. Command(resume=...) 恢复执行

```python
# 第一次调用：图在 interrupt() 处暂停
try:
    graph.invoke(
        {"messages": [HumanMessage("删除所有文件")]},
        config=config,
    )
except:
    pass  # 图暂停，捕获异常

# 查看图停在哪里
state = graph.get_state(config)
print(state.next)  # ('human_approval',)

# 人工审批后恢复执行
result = graph.invoke(
    Command(resume="确认执行"),  # 把用户决定传回去
    config=config,               # 同一个 thread_id！
)
```

### 5. 完整图结构

```
START
  ↓
assess（风险评估）
  ↓
route_by_risk（条件判断）
  ↙              ↘
human_approval   execute（低风险直接执行）
（高风险暂停）
  ↓
execute
  ↓
END
```

### 6. State 初始值的坑

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    risk_level: str
    approved: bool   # 初始值是 False！

# 低风险路径跳过 human_approval，approved 还是 False
# execute_action 看到 approved=False 就取消了！
```

**解决方案：在评估节点里根据风险级别设置初始 approved：**

```python
def assess_risk(state: State):
    is_high_risk = ...
    return {
        "risk_level": "high" if is_high_risk else "low",
        "approved": not is_high_risk,  # 低风险直接批准！
    }
```

### 7. 生产环境的持久化

```python
# 开发测试
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()  # 内存，重启丢失❌

# 本地持久化
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")  # SQLite ✅

# 生产环境
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")  # PG ✅
```

**用户几小时后回复也没问题，State 存在数据库里，服务重启后用同一个 thread_id 恢复。**

---

## 面试考点

**Q：什么是 Human-in-the-Loop？为什么需要它？**  
答：在 Agent 执行危险操作前强制暂停，等待人工确认后再继续。防止 Agent 误解用户意图导致误删文件、误发邮件等不可逆操作。生产环境 Agent 必备的安全机制。

**Q：HIL 的技术实现原理？**  
答：`interrupt()` 触发时把当前 State 存到 checkpointer，返回给调用方，图停止执行。用户确认后用 `Command(resume=value)` 传入决定，LangGraph 从 checkpointer 恢复 State，继续执行剩余节点。

**Q：HIL 期间服务器重启怎么办？**  
答：用持久化 checkpointer（SqliteSaver 或 PostgresSaver）替代 MemorySaver。State 存在数据库里，服务重启后用同一个 thread_id 从数据库恢复，用户几小时甚至几天后回复都能继续。

**Q：interrupt() 和普通的 input() 等待有什么区别？**  
答：input() 会阻塞进程，无法处理其他请求。interrupt() 暂停图的执行并返回，服务进程继续运行可以处理其他请求，用户回复时再恢复这个图的执行，适合生产环境的异步场景。

---

## 今日文件结构
```
week3/day16/
└── 01_hitl.py  ✅ interrupt()暂停、Command(resume)恢复、风险评估、持久化说明
```

---

## 明天预告 — Day 17：工具设计规范 + MCP 协议
- Tool 的 description 为什么是最重要的字段
- 工具设计的五个原则
- MCP（Model Context Protocol）是什么
- 用 MCP 把工具标准化暴露给任何 Agent