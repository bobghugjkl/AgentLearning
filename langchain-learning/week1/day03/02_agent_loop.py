import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
# ── 工具函数 ──────────────────────────────────────────
def get_weather(city: str) -> str:
    """查天气"""
    fake_data = {
        "北京": "晴天，25°C，东风3级",
        "上海": "多云，22°C，南风2级",
        "广州": "小雨，28°C，西风1级",
    }
    return fake_data.get(city, f"{city}暂无数据")

def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "计算出错"

# ── 合法工具字典 ───────────────────────────────────────
available_tools = {
    "get_weather": get_weather,
    "calculate": calculate,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",  # 模型靠这句话决定要不要调用
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，比如：北京、上海",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "做计算",  # 模型靠这句话决定要不要调用
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "计算数学表达式",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

def run_agent(user_input: str):
    print(f"\n用户：{user_input}")
    print("=" * 40)
    messages = [{"role": "user", "content": user_input}]

    # ── Agent 循环：一直跑到模型不再调用工具为止 ──
    while True:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # 情况1：模型不需要调工具，直接给出最终答案
        if finish_reason == "stop":
            print(f"\nAgent：{message.content}")
            break

        # 情况2：模型要调工具
        if finish_reason == "tool_calls":
            messages.append(message)  # 先把模型这轮回复存起来

            # 可能同时调多个工具，逐个执行
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"调用工具：{func_name}，参数：{func_args}")

                # 执行工具
                if func_name in available_tools:
                    result = available_tools[func_name](**func_args)
                else:
                    result = f"错误：工具 {func_name} 不存在"

                print(f"工具结果：{result}")

                # 把结果塞回 messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

# ── 测试 ──────────────────────────────────────────────
run_agent("北京和上海今天天气怎么样？另外帮我算一下 123 * 456 等于多少")