# Day 03 复盘笔记 — Function Calling 与 Agent 雏形

## 今天学了什么

### 1. Function Calling 的本质
- 模型本身不能上网、不能执行代码、不能查数据库
- Function Calling 让模型能"下单"调用外部工具
- **模型负责thinking（决定调什么），代码负责doing（真正执行）**

### 2. 完整流程（两次请求）
```
用户提问
    ↓
第一次请求：模型返回 tool_calls（我要调哪个工具、传什么参数）
    ↓
我们的代码执行工具，拿到结果
    ↓
第二次请求：把结果用 role="tool" 塞回 messages
    ↓
模型给出最终自然语言回答
```

### 3. tools 列表结构
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气",  # ← 最重要！模型靠这个决定要不要调
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称",
                    }
                },
                "required": ["city"],
            },
        },
    }
]
```

### 4. tool_choice 参数
| 值 | 含义 |
|----|------|
| `"auto"` | 模型自己决定要不要调工具 |
| `"none"` | 禁止调任何工具，直接回答 |
| `"required"` | 必须调工具，调哪个模型决定 |
| `{"type": "function", "function": {"name": "xxx"}}` | 强制只调某一个工具 |

### 5. finish_reason 含义
| 值 | 含义 |
|----|------|
| `"stop"` | 正常结束，模型给出最终回答 |
| `"tool_calls"` | 模型要调工具，还没结束 |
| `"length"` | token 用完被截断，回答不完整 |

### 6. available_tools 字典技巧
```python
# 函数作为值存进字典，动态调用任意工具
available_tools = {
    "get_weather": get_weather,
    "calculate": calculate,
}

# 一行搞定，不用写100个 if-else
result = available_tools[func_name](**func_args)
```

### 7. Agent 循环
```python
while True:
    response = client.chat.completions.create(...)
    finish_reason = response.choices[0].finish_reason

    if finish_reason == "stop":
        # 模型不需要工具了，给出最终回答
        print(message.content)
        break

    if finish_reason == "tool_calls":
        # 执行工具，结果塞回 messages，继续循环
        for tool_call in message.tool_calls:
            result = available_tools[func_name](**func_args)
            messages.append({"role": "tool", ...})
```

**为什么用 while True 不用固定次数？**  
因为工具调用次数不确定，固定次数可能不够用。

### 8. Function Calling vs 直接输出 JSON
| | 直接输出JSON | Function Calling |
|--|------------|-----------------|
| 格式稳定性 | 模型可能输出格式乱 | 模型层强制保证结构 |
| 多工具支持 | 自己解析判断 | tool_call_id 精确对应 |
| 并行调用 | 做不到 | 一次返回多个tool_calls |

---

## 关键认知

> **大模型决定调什么，我们决定能调什么。**
> 就像餐厅点菜——顾客（模型）自己点，但菜单（tools）是我们定的。

> **`description` 是最重要的字段。**
> 模型靠 description 决定要不要调这个工具，写不好模型调错工具，整个 Agent 失效。

---

## 面试考点

**Q：Function Calling 的流程是什么？**  
答：两次请求。第一次模型返回 tool_calls（决定调哪个工具传什么参数），我们的代码执行工具拿到结果，第二次把结果用 role="tool" 塞回 messages，模型给出最终回答。

**Q：模型会自己执行工具吗？**  
答：不会。模型只负责决定调什么工具、传什么参数，真正执行是我们的代码。模型是大脑，代码是手脚。

**Q：Tool 的 description 不写会怎样？**  
答：模型无法判断什么时候该调这个工具，可能该调不调、或者调错工具，整个 Agent 失效。description 是工具设计最重要的部分。

**Q：Agent 循环为什么用 while True？**  
答：工具调用次数不确定，可能一次也可能多次。用 while True 直到 finish_reason=="stop" 才 break，能处理任意次数的工具调用。

**Q：Function Calling 和直接让模型输出 JSON 的区别？**  
答：直接输出 JSON 格式不稳定、不支持并行调用、没有 tool_call_id 对应关系。Function Calling 是模型层的标准协议，格式有保证，支持一次返回多个 tool_calls 并行执行。

**Q：`**func_args` 是什么意思？**  
答：Python 解包语法，把字典拆成关键字参数。`func(**{"city": "北京"})` 等价于 `func(city="北京")`，支持任意参数数量，不用手动一个个传。

---

## 今日文件结构
```
day03/
├── 01_function_calling.py  ✅ Function Calling 四步流程
└── 02_agent_loop.py        ✅ 完整 Agent 循环、多工具并行调用
```

---

## 明天预告 — Day 04：正式进入 LangChain
- 为什么需要 LangChain（手写 Agent 的痛点）
- LangChain 的包结构：core / langchain / community 分别是什么
- `init_chat_model` 一行接入任意模型
- Runnable 协议：LangChain 的核心设计思想