# Day 17 复盘笔记 — 工具设计规范 + MCP 协议

## 今天学了什么

### 1. 工具设计五原则

#### 原则1：description 要清晰具体（最重要！）
```python
# ❌ 差的 description
@tool
def get_weather(city: str) -> str:
    """天气"""  # 模型不知道能干什么

# ✅ 好的 description
@tool
def get_weather(city: str) -> str:
    """获取指定城市的实时天气信息，包括温度、天气状况和风力等级。
    适用于用户询问某城市天气、温度、是否需要带伞等问题。
    
    Args:
        city: 城市名称，如"北京"、"上海"、"东京"
    """
```

**模型靠 description 决定要不要调用，不是靠函数名！**

#### 原则2：参数名要语义化
```python
# ❌ 差的参数名
def search(q: str, n: int): ...

# ✅ 好的参数名
def search(query: str, limit: int): ...
```

#### 原则3：返回值要截断
```python
@tool
def search_database(query: str) -> str:
    results = db.search(query)
    return str(results)[:500]  # 截断！防止 token 爆炸
```

#### 原则4：危险操作加 HIL
```python
# 发邮件、删除、转账等不可逆操作必须加人工确认
# 参考 Day 16 的 interrupt() 机制
```

#### 原则5：工具要幂等
```python
# 幂等：执行多次结果一样
def get_weather(city):  # 查询操作，天然幂等 ✅
    return "晴天25°C"

# 不幂等：执行多次有副作用
def send_email(to, content):  # 发邮件，调3次发3封 ❌
    email.send(...)
```

**不幂等的工具必须加去重或 HIL 机制。**

### 2. MCP（Model Context Protocol）

**是什么：** Anthropic 2024 年推出的工具标准化协议，现已成为行业标准。

**解决什么问题：**
```
以前：每个框架/语言要重写一遍工具
MCP：一次写好，任何 Agent 都能调用

就像 Type-C 统一了充电接口
MCP 统一了 AI 工具接口
```

**支持 MCP 的产品：** Claude Desktop、VS Code、Cursor、LangChain、任何 OpenAI 兼容框架。

### 3. MCP Server 写法

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("我的工具箱")

@mcp.tool()  # 用 @mcp.tool() 替代 @tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。
    
    Args:
        city: 城市名称
    """
    return "晴天25°C"

if __name__ == "__main__":
    mcp.run()
```

### 4. MCP Client 连接

```python
import asyncio
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 加载 MCP 工具，自动转成 LangChain 格式
            tools = await load_mcp_tools(session)
            
            # 正常使用
            agent = create_react_agent(model, tools)
            result = await agent.ainvoke({"messages": [...]})

asyncio.run(main())
```

### 5. 异步代码关键概念

| 语法 | 含义 |
|------|------|
| `async def` | 声明异步函数 |
| `await` | 等待异步操作完成，等待期间让出CPU |
| `async with` | 异步上下文管理器，自动关闭资源 |
| `asyncio.run()` | 启动事件循环，运行异步函数 |
| `ainvoke()` | invoke 的异步版本 |

### 6. @tool vs MCP 对比

| | @tool 直接写 | MCP Server |
|--|------------|-----------|
| 适用范围 | 当前项目 | 任何语言/框架 |
| 解耦程度 | 和Agent代码耦合 | 独立部署 |
| 复用性 | 低 | 高 |
| 复杂度 | 简单 | 稍复杂 |
| 适合场景 | 项目内部工具 | 多Agent共用工具 |

**什么时候用 MCP：**
- 工具需要被多个 Agent 共用
- 需要被不同语言调用
- 对接 Claude Desktop/Cursor 等产品

---

## 面试考点

**Q：工具的 description 为什么最重要？**  
答：模型靠 description 决定要不要调用这个工具，以及理解工具的能力范围。函数名模型可能根本不看。description 写得差，模型会不调用或调错工具，整个 Agent 失效。

**Q：什么是幂等？为什么 Agent 工具需要关注幂等？**  
答：幂等是执行一次和多次结果相同。Agent 可能因为网络超时、模型重试等原因重复调用工具，不幂等的工具（发邮件、转账、删除）会产生重复副作用。不幂等的工具必须加 HIL 或去重机制。

**Q：MCP 是什么？解决什么问题？**  
答：Model Context Protocol，Anthropic 2024年推出的工具标准化协议。解决不同框架/语言的工具不兼容问题，一次写好，任何支持MCP的Agent（LangChain、Claude、Cursor等）都能调用。

**Q：MCP Server 和直接写 @tool 有什么区别？**  
答：@tool 只能在当前Python项目用，和Agent代码耦合。MCP Server 独立部署，任何语言/框架都能调用，适合多Agent共用的工具或需要对接Claude Desktop等产品的场景。

---

## 今日文件结构
```
week3/day17/
├── 01_tool_design.py  ✅ 工具设计五原则、好坏工具对比
├── 02_mcp_server.py   ✅ MCP Server，注册工具
└── 03_mcp_client.py   ✅ MCP Client，异步连接调用
```

---

## 明天预告 — Day 18：Plan-and-Execute Agent
- ReAct vs Plan-and-Execute 的区别
- Planner 先规划，Executor 按计划执行
- 什么时候用 Plan-and-Execute？
- 用 LangGraph 实现完整的规划执行流程