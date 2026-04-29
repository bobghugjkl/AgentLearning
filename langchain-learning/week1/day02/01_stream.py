import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

print("=== 流式输出 ===\n")

# stream=True 开启流式
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用100字介绍一下乃木坂46"}],
    temperature=0.7,
    max_tokens=256,
    stream=True,   # ← 关键！
)
full_response = ""
# 逐块接收并打印
for chunk in stream:
    # 每个 chunk 里的内容在这里
    delta = chunk.choices[0].delta.content
    if delta:                    # delta 可能是 None，要判断
        print(delta, end="", flush=True)  # end="" 不换行，flush 立即输出
        full_response += delta
print(f"\n\n完整内容：{full_response}")

print("\n\n=== 结束 ===")