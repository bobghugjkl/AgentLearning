# 多轮对话
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
print(os.getenv("DEEPSEEK_API_KEY"))
client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

#手动维护对话历史
messages = [
    {"role": "system", "content": "你是斋藤飞鸟。"},
    {"role": "user", "content": "斋藤飞鸟是谁?"}
]

#第一轮
resp1 = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    temperature=0.3,
    max_tokens=256,
)
answer1 = resp1.choices[0].message.content
print(f"第一轮回答：\n{answer1}")

# 关键：把模型回答塞回 messages，它才能"记住"
messages.append({"role":"assistant","content":answer1})
messages.append({"role": "user","content": "西野七濑是谁？"})
# 第二轮
resp2 = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    temperature=0.3,
    max_tokens=256,
)
print(f"\n第二轮回答：\n{resp2.choices[0].message.content}")

print(f"\n第二轮请求时 messages 共 {len(messages) + 1} 条")
print("对话越长，每次带的历史越多，token消耗越大")