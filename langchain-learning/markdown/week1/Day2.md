# Day 02 复盘笔记 — 流式输出与 SSE

## 今天学了什么

### 1. 流式输出的本质
- 普通请求：等全部生成完，一次性返回
- 流式请求：生成一块，发一块，用户立刻看到内容
- 两种方式服务器生成总时间一样，但用户**感知**完全不同

### 2. TTFT（Time To First Token）
- 首个 token 到达客户端的延迟
- 是衡量 LLM 服务质量的核心指标
- 流式输出让 TTFT 从"等全部完成"变成"等第一个字"
- 生产环境 TTFT < 1s 是基本要求

### 3. stream=True 的用法
```python
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    stream=True,   # 开启流式
)

full_response = ""
for chunk in stream:
    delta = chunk.choices[0].delta.content  # 注意是 delta 不是 message
    if delta:                               # delta 可能是 None，要判断
        print(delta, end="", flush=True)
        full_response += delta              # 拼接完整内容
```

**普通请求 vs 流式请求的区别：**
| | 普通请求 | 流式请求 |
|--|---------|---------|
| 取内容 | `message.content` | `delta.content` |
| 返回方式 | 一次性 | 逐块 |
| 需要循环 | 不需要 | 需要 for 循环 |

### 4. yield 生成器
- `return`：函数结束，返回一个值
- `yield`：函数暂停，返回一个值，下次继续从这里执行
- 生成器天生适合流式场景，生成一块 yield 一块

```python
def generate(question: str):
    stream = client.chat.completions.create(...)
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta  # 生成一块，发一块
```

### 5. FastAPI 流式接口
```python
from fastapi.responses import StreamingResponse

@app.get("/chat")
def chat(question: str):
    return StreamingResponse(
        generate(question),      # 传入生成器函数
        media_type="text/plain",
    )
```

### 6. SSE vs WebSocket
| | SSE | WebSocket |
|--|-----|-----------|
| 方向 | 单向（服务器→客户端） | 双向 |
| 协议 | 普通 HTTP | WS 协议 |
| CDN/Nginx | 天然支持 | 需要额外配置 |
| 适合场景 | LLM流式、消息推送 | 聊天室、实时游戏 |

**LLM 流式输出选 SSE** 因为：用户发问是一次性的，不需要双向通信。

---

## 今天遇到的问题

### 问题1：PowerShell 的 curl 不是真正的 curl
**原因：** PowerShell 里 `curl` 是 `Invoke-WebRequest` 的别名，不支持 `-N` 参数  
**解决：** 用 `curl.exe` 或者用 Git Bash

### 问题2：浏览器看不到逐字效果
**原因：** 浏览器会缓存 HTTP 响应，攒够了再显示  
**解决：** 用 curl `-N` 参数禁用缓冲，或者前端用 EventSource/fetch+ReadableStream

### 问题3：多余的 import 导致报错
**原因：** IDE 自动补全加了 `from sympy.abc import delta`  
**解决：** 写完代码检查 import，删掉无关的

---

## 面试考点

**Q：什么是 TTFT？为什么重要？**  
答：TTFT（Time To First Token）是从发出请求到收到第一个 token 的时间。LLM 生成慢，TTFT 决定用户感知到的响应速度，生产环境要求 < 1s。

**Q：SSE 和 WebSocket 的区别？LLM 流式用哪个？**  
答：SSE 是单向推送（服务器→客户端），基于 HTTP，CDN 友好；WebSocket 是双向通信。LLM 流式输出用 SSE，因为用户发问是一次性的，不需要双向，而且 SSE 更简单、部署更友好。

**Q：流式输出和普通输出，服务器生成速度一样吗？**  
答：一样，生成总时间相同。流式的优势是用户更早看到内容（TTFT 更低），体验更好，不是生成更快。

**Q：yield 和 return 的区别？**  
答：return 函数执行完就结束；yield 让函数暂停返回一个值，下次继续执行，适合分批生产数据的流式场景。

---

## 今日文件结构
```
day02/
├── 01_stream.py        ✅ 流式输出基础、delta拼接
└── 02_stream_api.py    ✅ FastAPI流式接口、StreamingResponse、yield生成器
```

---

## 明天预告 — Day 03：Function Calling
- 什么是 Function Calling（工具调用）
- 不用任何框架，纯 SDK 实现一个会查天气的 Agent
- 理解 tool_calls 的结构
- 这是 LangChain Agent 的底层原理，必须搞懂