import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
# ── 第一步：定义工具 ──────────────────────────────────
# 用 JSON Schema 告诉模型：你有哪些工具、每个工具需要什么参数

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，比如北京上海"
                    }
                },
                "required": ["city"],
            },
        },
    }
]

# print("工具定义完成，共", len(tools), "个工具")
# print(json.dumps(tools, ensure_ascii=False, indent=2))

# ── 第二步：发请求，让模型决定要不要调工具 ──────────────

messages = [
    {"role": "user", "content": "北京今天天气怎么样？"}
]

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    tools=tools,           # 把工具列表传给模型
    tool_choice="auto",    # auto = 模型自己决定要不要调
)

# 看看模型返回了什么
message = response.choices[0].message
print("\n=== 模型返回 ===")
print("内容:", message.content)
print("工具调用:", message.tool_calls)

# ── 第三步：我们来"假装"执行这个工具 ──────────────────
def get_weather(city: str) -> str:
    """模拟天气查询，真实场景这里调真实API"""
    fake_data = {
        "北京": "晴天，25°C，东风3级",
        "上海": "多云，22°C，南风2级",
        "广州": "小雨，28°C，西风1级",
    }
    return fake_data.get(city, f"{city}的天气数据暂无")

# 解析模型返回的工具调用
tool_call = message.tool_calls[0]
func_name = tool_call.function.name
func_args = json.loads(tool_call.function.arguments)  # 字符串→字典

print(f"\n=== 执行工具 ===")
print(f"函数名: {func_name}")
print(f"参数: {func_args}")

# 执行函数
result = get_weather(**func_args)
print(f"结果: {result}")

# ── 第四步：把工具结果告诉模型，让它给出最终回答 ──────
# 注意 messages 要把之前所有内容都带上

messages.append(message)  # 把模型上一轮的回复加进去（包含tool_calls）
messages.append({
    "role": "tool",                        # 注意：这里是 tool 角色
    "tool_call_id": tool_call.id,          # 对应哪次工具调用
    "content": result,                     # 工具执行的结果
})

# 再次请求模型，让它根据工具结果给出最终回答
final_response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    tools=tools,
)

print("\n=== 最终回答 ===")
print(final_response.choices[0].message.content)