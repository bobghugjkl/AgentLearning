# Day 05 复盘笔记 — 结构化输出

## 今天学了什么

### 1. 为什么需要结构化输出
模型自由输出格式不稳定：
```
第一次："北京今天晴天，25°C，非常适合外出"
第二次："今天北京的天气是晴天，温度25摄氏度"
第三次："🌤 北京 | 晴 | 25°C"
```
格式不稳定 → 解析代码崩溃 → 生产环境必须强制结构化输出。

### 2. Pydantic BaseModel
```python
from pydantic import BaseModel, Field

class Weather(BaseModel):
    city: str = Field(description="城市名称")
    weather: str = Field(description="天气状况")
    temperature: float = Field(description="温度，摄氏度")
    suggestion: str = Field(description="出行建议，一句话")
```
- `Field(description=...)` 告诉模型每个字段填什么
- 类型自动校验：`temperature: float` 会把 "25" 自动转成 25.0
- 所有字段默认 `required=True`

### 3. with_structured_output（核心）
```python
structured_model = model.with_structured_output(Weather)
result = structured_model.invoke("北京今天天气怎么样？")

# 返回的直接是 Weather 对象，不是字符串
print(result.city)         # "北京"
print(result.temperature)  # 25.0（float，不是字符串）
```

**底层原理：**
1. LangChain 把 Weather 类转成 JSON Schema 传给模型
2. 模型按 Schema 输出 JSON
3. LangChain 把 JSON 自动转成 Weather 对象返回

### 4. 嵌套结构
```python
from typing import List

class Person(BaseModel):
    name: str = Field(description="人物姓名")
    role: str = Field(description="人物身份")
    fact: str = Field(description="关键事实")

class ArticleInfo(BaseModel):
    topic: str = Field(description="文章主题")
    persons: List[Person] = Field(description="人物列表")  # 嵌套！
    key_takeaway: str = Field(description="核心结论")
```

`List[Person]` = 列表，每个元素都是 Person 对象。
LangChain 自动递归处理嵌套类，不需要单独传 Person。

```python
for person in result.persons:
    print(f"{person.name}：{person.fact}")
```

### 5. with_retry 容错
```python
reliable_chain = chain.with_retry(
    stop_after_attempt=3,  # 最多试3次
)
```
- 第一次失败 → 自动重试
- 成功了 → 直接返回，不再重试
- 3次都失败 → 彻底报错

适用场景：网络抖动、模型偶发格式错误、API 限流。

### 6. 完整 chain 组合
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是信息抽取助手"),
    ("human", "从下面文字抽取信息：\n\n{text}"),
])

structured_model = model.with_structured_output(ArticleInfo)
chain = prompt | structured_model  # 注意：不需要 StrOutputParser
```

---

## 关键认知

> **结构化输出不是可选项，是生产环境标配。**
> 自由文本解析是 Bug 之源，永远要求模型输出 JSON。

> **Field 的 description 和 Tool 的 description 一样重要。**
> 模型靠 description 理解每个字段填什么，写不好输出就会乱。

> **temperature=0 用于结构化输出。**
> 需要稳定格式时关掉随机性，不然模型可能"发挥"出奇怪的格式。

---

## 面试考点

**Q：with_structured_output 的底层原理？**  
答：LangChain 把 Pydantic 类转成 JSON Schema，通过 Function Calling 或 JSON mode 传给模型，模型按 Schema 输出 JSON，LangChain 再把 JSON 转成 Pydantic 对象返回。

**Q：为什么用 Pydantic 而不是直接让模型输出 JSON 字符串？**  
答：Pydantic 提供类型校验和自动转换，`temperature: float` 会把字符串自动转成数字；有嵌套结构支持；返回的是可以直接用属性访问的 Python 对象，不需要手动解析。

**Q：模型输出格式不对怎么处理？**  
答：用 `.with_retry(stop_after_attempt=3)` 加重试，失败自动重试最多3次。生产环境还可以加 fallback 降级到更稳定的模型。

**Q：List[Person] 是什么意思？**  
答：Python typing 语法，表示一个列表，列表里每个元素都是 Person 类型。LangChain 会自动递归处理嵌套的 Pydantic 类，生成完整的嵌套 JSON Schema。

---

## 今日文件结构
```
day05/
├── 01_structured_output.py  ✅ with_structured_output、Pydantic基础
└── 02_extract.py            ✅ 嵌套结构、信息抽取、with_retry
```

---

## 明天预告 — Day 06：LangChain Memory 与对话管理
- 为什么 LangChain 的旧 Memory 被废弃了
- 新的做法：用 LangGraph Checkpointer 管理记忆
- 对话历史的几种压缩策略
- 实现一个有记忆的聊天机器人