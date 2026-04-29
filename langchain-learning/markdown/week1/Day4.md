# Day 04 复盘笔记 — 正式进入 LangChain

## 今天学了什么

### 1. 为什么需要 LangChain
手写 Agent 的痛点：
- 自己管理 messages 数组
- 自己判断 finish_reason
- 自己循环执行工具
- 自己处理错误重试
- 换个模型要改一堆地方

LangChain 把这些全部封装好，只需关心业务逻辑。

### 2. LangChain 包结构
```
langchain-core      ← 核心接口，最轻量，必装
langchain           ← 主包，常用组件
langchain-openai    ← OpenAI / DeepSeek 支持
langchain-deepseek  ← DeepSeek 专用包（单独装）
langchain-community ← 第三方集成（通义、向量库等）
```
**用什么装什么，不用的不装。**

### 3. init_chat_model
```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7,
)
```
一行初始化任意模型，换模型只需改前两个参数。

### 4. Runnable 协议
LangChain 所有组件都实现同一套接口：
```python
model.invoke("你好")           # 单次调用
model.stream("你好")           # 流式输出
model.batch(["你好", "再见"])  # 批量调用
```
统一接口，随意组合，这是 LangChain 最核心的设计思想。

### 5. 消息类
```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 对应关系：
SystemMessage → {"role": "system",    "content": "..."}
HumanMessage  → {"role": "user",      "content": "..."}
AIMessage     → {"role": "assistant", "content": "..."}
ToolMessage   → {"role": "tool",      "content": "..."}
```
**好处：** 类型安全，不会把 role 名字写错；`model.invoke()` 返回的直接是 `AIMessage`，可以直接塞回 messages。

### 6. LCEL 管道
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{language}翻译助手，只输出译文。"),
    ("human", "{text}"),
])

parser = StrOutputParser()  # 把 AIMessage 转成纯字符串

chain = prompt | model | parser  # 管道符组合

result = chain.invoke({
    "language": "日语",
    "text": "今天天气真好",
})
```

**数据流动：**
```
invoke({"language": "日语", "text": "今天天气真好"})
        ↓
prompt：填充模板 → 生成 messages 数组
        ↓
model：调用 DeepSeek → 返回 AIMessage
        ↓
parser：提取 content → 返回纯字符串
```

**ChatPromptTemplate 的价值：**
模板复用，同一个 chain 换个参数就能复用：
```python
chain.invoke({"language": "英语", "text": "今天天气真好"})
chain.invoke({"language": "韩语", "text": "今天天气真好"})
```

---

## 面试考点

**Q：LangChain 的包为什么要拆分成多个？**  
答：避免臃肿。如果是一个大包，用 DeepSeek 也要装 OpenAI、通义、Anthropic 的依赖。拆包后用什么装什么，项目更轻量。

**Q：Runnable 协议是什么？有什么价值？**  
答：LangChain 所有组件统一实现 invoke/stream/batch/ainvoke 接口。好处是统一接口随意组合，prompt、model、parser、chain、agent 都能用同样方式调用，也支持自动并发、流式、重试、LangSmith trace 注入。

**Q：LCEL 管道 `|` 是什么原理？**  
答：Python 的 `__or__` 运算符重载。每个组件实现了 `__or__` 方法，`prompt | model` 返回一个新的 Runnable，数据从左流向右，前一个的输出作为后一个的输入。

**Q：StrOutputParser 的作用？**  
答：把 model 返回的 AIMessage 对象提取出 content 字段，转成纯字符串。简化下游处理，不用每次写 `response.content`。

**Q：ChatPromptTemplate 和直接写 messages 有什么区别？**  
答：ChatPromptTemplate 支持变量占位符 `{variable}`，可以复用模板，invoke 时传不同参数生成不同 messages，不用每次手动构造。

---

## 今日文件结构
```
day04/
├── 01_init_model.py  ✅ init_chat_model、invoke、stream
├── 02_messages.py    ✅ 消息类、多轮对话
└── 03_lcel.py        ✅ LCEL管道、ChatPromptTemplate、StrOutputParser
```

---

## 明天预告 — Day 05：Output Parsers 与结构化输出
- 为什么生产环境要强制结构化输出
- PydanticOutputParser：用模型类定义输出格式
- with_structured_output：最推荐的现代写法
- JSON 解析失败怎么处理